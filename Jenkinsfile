elifeLibrary {
    def isNew
    def candidateVersion
    def commit

    stage 'Checkout', {
        checkout scm
        commit = elifeGitRevision()
    }

    node('containers-jenkins-plugin') {
        stage 'Build images', {
            checkout scm
            dockerComposeBuild(commit)
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

        stage 'Project tests (PY2)', {
            try {
                sh "IMAGE_TAG=${commit} " +
                    "docker-compose -f docker-compose.yml -f docker-compose.ci.yml " +
                    "run sciencebeam-utils-py2 ./project_tests.sh"
            } finally {
                sh 'docker-compose down -v'
            }
        }

        stage 'Project tests (PY3)', {
            try {
                sh "IMAGE_TAG=${commit} " +
                    "docker-compose -f docker-compose.yml -f docker-compose.ci.yml " +
                    "run sciencebeam-utils-py3 ./project_tests.sh"
            } finally {
                sh 'docker-compose down -v'
            }
        }

        elifeMainlineOnly {
            stage 'Push release', {
                isNew = sh(script: "git tag | grep v${candidateVersion}", returnStatus: true) != 0
                if (isNew) {
                    sh "IMAGE_TAG=${commit} " +
                        "docker-compose -f docker-compose.yml -f docker-compose.ci.yml run " +
                        "sciencebeam-utils-py2 twine upload dist/*"
                }
            }
        }

    }

    elifeMainlineOnly {
        stage 'Merge to master', {
            elifeGitMoveToBranch commit, 'master'
            if (isNew) {
                sh "git tag v${candidateVersion} && git push origin v${candidateVersion}"
            }
        }
    }
}
