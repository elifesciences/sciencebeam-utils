import groovy.json.JsonSlurper

@NonCPS
def jsonToPypirc(String jsonText, String sectionName) {
    def credentials = new JsonSlurper().parseText(jsonText)
    echo "Username: ${credentials.username}"
    return "[${sectionName}]\nusername=${credentials.username}\npassword=${credentials.password}"
}

def withPypiCredentials(String env, String sectionName, doSomething) {
    try {
        File('.pypirc').write jsonToPypirc(sh(
            script: "vault.sh kv get -format=json secret/containers/pypi/${env} | jq .data.data",
            returnStdout: true
        ).trim(), sectionName)
        doSomething()
    } finally {
        sh 'echo > .pypirc'
    }
}

elifePipeline {
    def candidateVersion
    def commit

    node('containers-jenkins-plugin') {
        stage 'Checkout', {
            checkout scm
            commit = elifeGitRevision()
        }

        stage 'Test release', {
            withPypiCredentials 'staging', 'pypitest', {
                sh 'ls -l .pypirc'
            }
            // try {
            //     echo "Reading credentials"
            //     def pypirc = jsonToPypirc(sh(
            //         script: 'vault.sh kv get -format=json secret/containers/pypi/staging | jq .data.data',
            //         returnStdout: true
            //     ).trim(), "pypitest")
            //     // sh 'ls -l .pypirc.credentials'
            //     // def credentials = new JsonSlurper().parseFile('.pypirc.credentials')
            //     echo "Read credentials"
            //     // echo "Username: ${credentials.username}"
            //     // {
            //     //   "password": "...",
            //     //   "username": "..."
            //     // }
            //     // do push to test.pypi.org
            // } finally {
            //     sh 'echo > .pypirc.credentials'
            // }
        }

        stage 'Build images', {
            checkout scm
            def version 
            if (env.TAG_NAME) {
                version = env.TAG_NAME - 'v'
            } else {
                version = 'develop'
            }
            withEnv(["VERSION=${version}"]) {
                dockerComposeBuild(commit)
            }
            try {
                candidateVersion = sh(
                    script: (
                        "IMAGE_TAG=${commit} " +
                        "docker-compose -f docker-compose.yml -f docker-compose.ci.yml run " +
                        "sciencebeam-utils-py2 ./print_version.sh"
                    ),
                    returnStdout: true
                ).trim()
                echo "Candidate version: v${candidateVersion}"
            } finally {
                sh 'docker-compose down -v'
            }
        }

        stage 'Project tests', {
            try {
                parallel(['Project tests (PY2)': {
                    withCommitStatus({
                        sh "IMAGE_TAG=${commit} " +
                            "docker-compose -f docker-compose.yml -f docker-compose.ci.yml " +
                            "run sciencebeam-utils-py2 ./project_tests.sh"
                    }, 'project-tests/py2', commit)
                },
                'Project tests (PY3)': {
                    withCommitStatus({
                        sh "IMAGE_TAG=${commit} " +
                            "docker-compose -f docker-compose.yml -f docker-compose.ci.yml " +
                            "run sciencebeam-utils-py3 ./project_tests.sh"
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

        elifeTagOnly { tag ->
            stage 'Push release', {
                try {
                    sh 'vault.sh kv get -format json secret/containers/pypi/prod | jq .data.data > .pypirc.credentials'
                    sh "IMAGE_TAG=${commit} " +
                        "docker-compose -f docker-compose.yml -f docker-compose.ci.yml run " +
                        "sciencebeam-utils-py2 twine upload dist/*"
                } finally {
                    sh 'echo > .pypirc.credentials'
                }
            }
        }
    }
}
