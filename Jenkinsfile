elifeLibrary {
    def commit
    stage 'Checkout', {
        checkout scm
        commit = elifeGitRevision()
    }

    node('containers-jenkins-plugin') {
        stage 'Build images', {
            checkout scm
            dockerComposeBuild(commit)
        }

        stage 'Project tests', {
            try {
                sh "IMAGE_TAG=${commit} docker-compose run --rm sciencebeam-utils ./project_tests.sh"
            } finally {
                sh 'docker-compose down -v'
            }
        }
    }

    elifeMainlineOnly {
        stage 'Approval', {
            elifeGitMoveToBranch commit, 'approved'
        }
    }
}
