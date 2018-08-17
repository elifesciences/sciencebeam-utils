elifeLibrary {
    def commit
    stage 'Checkout', {
        checkout scm
        commit = elifeGitRevision()
    }

    node('containers-jenkins-plugin') {
        def candidateVersion
        stage 'Build images', {
            checkout scm
            dockerComposeBuild(commit)
            try {
                candidateVersion = sh(script: "IMAGE_TAG=${commit} docker-compose run --rm sciencebeam-utils ./print_version.sh", returnStdout: true).trim()
                echo "Candidate version: v${candidateVersion}"
            } finally {
                sh 'docker-compose down -v'
            }
        }

        stage 'Project tests', {
            try {
                sh "IMAGE_TAG=${commit} docker-compose run --rm sciencebeam-utils ./project_tests.sh"
            } finally {
                sh 'docker-compose down -v'
            }
        }

        stage 'Push release', {
            // def isNew = sh(script: "git tag | grep v${candidateVersion}", returnStatus: true) != 0
            // if (isNew) {
            //     sh "git tag v${candidateVersion} && git push origin v${candidateVersion}"
            //     sh "twine upload dist/*"
            // }
        }

    }

    elifeMainlineOnly {
        stage 'Approval', {
            elifeGitMoveToBranch commit, 'approved'
        }
    }
}
