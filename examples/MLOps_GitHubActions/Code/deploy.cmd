az ml model deploy --name seer-svc --model seer:32 --compute-target sauron --inference-config inferenceconfig.json --deploy-config-file deployconfig.json --overwrite
REM local
REM az ml model deploy --name seer-local --model seer:33 --inference-config inferenceconfig.json --deploy-config-file deployconfiglocal.json --overwrite