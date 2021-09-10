# Manual github actions

This repo cointains a github action WorkFlow thats allows to trigger aome Jobs conditionaly.
* In a PR or Merge all workflow job will be triggered.
* Manually in : Actions -> Manual Triggered workflow -> ... workflow_dipatch event triggered -> Run Workflow , you can set a env variable thats select the jobs to trigger
    * deploy-dev: will be trigger the deploy dev job 
    * deploy-test: will be trigger the deploy test job
    * deploy-prd: will be trigger the deploy prd job
