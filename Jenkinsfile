import groovy.json.JsonSlurper

@NonCPS
def jsonToPypirc(String jsonText, String sectionName) {
    def credentials = new JsonSlurper().parseText(jsonText)
    echo "Username: ${credentials.username}"
    return "[${sectionName}]\nusername: ${credentials.username}\npassword: ${credentials.password}"
}

def withPypiCredentials(String env, String sectionName, doSomething) {
    try {
        writeFile(file: '.pypirc', text: jsonToPypirc(sh(
            script: "vault.sh kv get -format=json secret/containers/pypi/${env} | jq .data.data",
            returnStdout: true
        ).trim(), sectionName))
        doSomething()
    } finally {
        sh 'echo > .pypirc'
    }
}

elifePipeline {
    node('containers-jenkins-plugin') {
        def commit
        def version

        stage 'Checkout', {
            checkout scm
            commit = elifeGitRevision()
        }

        stage 'Build images', {
            checkout scm
            if (env.TAG_NAME) {
                version = env.TAG_NAME - 'v'
            } else {
                version = 'develop'
            }
            withEnv(["VERSION=${version}"]) {
                dockerComposeBuild(commit)
            }
            try {
                def actualVersion = sh(
                    script: (
                        "IMAGE_TAG=${commit} " +
                        "docker-compose -f docker-compose.yml -f docker-compose.ci.yml run " +
                        "sciencebeam-utils-py2 ./print_version.sh"
                    ),
                    returnStdout: true
                ).trim()
                echo "Actual version: v${actualVersion}"
            } finally {
                sh 'docker-compose down -v'
            }
        }

        stage 'Project tests', {
            try {
                parallel(['Project tests (PY2)': {
                    withCommitStatus({
                        sh "make IMAGE_TAG=${commit} NO_BUILD=y ci-test-py2"
                    }, 'project-tests/py2', commit)
                },
                'Project tests (PY3)': {
                    withCommitStatus({
                        sh "make IMAGE_TAG=${commit} NO_BUILD=y ci-test-py3"
                    }, 'project-tests/py3', commit)
                }])
            } finally {
                sh 'docker-compose down -v'
            }
        }

        elifeMainlineOnly {
            stage 'Merge to master', {
                elifeGitMoveToBranch commit, 'master'
            }
        }

        elifePullRequestOnly { prNumber ->
            stage 'Push package to test.pypi.org', {
                withPypiCredentials 'staging', 'testpypi', {
                    sh "make IMAGE_TAG=${commit} COMMIT=${commit} NO_BUILD=y ci-push-testpypi"
                }
            }
        }

        elifeTagOnly { tag ->
            stage 'Push release', {
                withPypiCredentials 'prod', 'pypi', {
                    sh "make IMAGE_TAG=${commit} VERSION=${version} NO_BUILD=y ci-push-pypi"
                }
            }
        }
    }
}
