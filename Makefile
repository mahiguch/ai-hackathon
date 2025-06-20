login:
	gcloud auth login
	gcloud auth application-default login

deploy:
	.venv/bin/python deployment/deploy.py --create

destroy:
	.venv/bin/python  deployment/deploy.py --delete --resource_id=5777388246195503104

quicktest:
	.venv/bin/python  deployment/deploy.py --quicktest --resource_id=5777388246195503104