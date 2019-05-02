elifeLibrary {
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

        elifeMainlineOnly {
            stage 'Merge to master', {
                elifeGitMoveToBranch commit, 'master'
            }
        }

        elifeTagOnly { tag ->
            stage 'Push release', {
                sh "IMAGE_TAG=${commit} " +
                    "docker-compose -f docker-compose.yml -f docker-compose.ci.yml run " +
                    "sciencebeam-utils-py2 twine upload dist/*"
            }
        }
    }
}
