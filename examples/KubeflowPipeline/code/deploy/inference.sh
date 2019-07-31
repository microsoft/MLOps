echo "test the deployment with a burrito image"
az ml service run -n fooddeployaci -d '{ "image": "https://www.exploreveg.org/files/2015/05/sofritas-burrito.jpeg" }' -w taco-workspace -g taco-rg
echo "test the deployment with a taco image"
az ml service run -n fooddeployaci -d '{ "image": "https://c1.staticflickr.com/5/4022/4401140214_f489c708f0_b.jpg" }' -w taco-workspace -g taco-rg
