rm -r data\prep
rm -r data\train
rm -r data\model
python prep.py -s data\food -t data\prep
python train.py -s data\prep -t data\train --epochs 10 --batch 32 --lr 0.0001
python register.py -s data\train -t data\model
