elifeLibrary {
    def commit
    stage 'Checkout', {
        checkout scm
        commit = elifeGitRevision()
    }

    stage 'Build image', {
        sh 'docker build -t elife/sciencebeam-utils .'
    }

    stage 'Run tests', {
        elifeLocalTests './project_tests.sh'
    }

    elifeMainlineOnly {
        stage 'Merge to master', {
            elifeGitMoveToBranch commit, 'master'
        }
    }
}
