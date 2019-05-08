import groovy.json.JsonSlurper

elifePipeline {
    def candidateVersion
    def commit

    node('containers-jenkins-plugin') {
        stage 'Checkout', {
            checkout scm
            commit = elifeGitRevision()
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

        stage 'Test release', {
            try {
                sh 'vault.sh kv get -format=json secret/containers/pypi/staging | jq .data.data > .pypirc.credentials'
                sh 'ls -l .pypirc.credentials'
                def credentials = new JsonSlurper().parseFile('.pypirc.credentials')
                echo "Username: ${credentials.username}"
                // {
                //   "password": "...",
                //   "username": "..."
                // }
                // do push to test.pypi.org
            } finally {
                sh 'echo > .pypirc.credentials'
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
