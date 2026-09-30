python main.py --dataset ./data/femgo --n-e-bins 35 --e-min 0.0 --e-max 0.7 \
  --n-dz-bins 12 --relax-steps 100 --reference-steps 300 \
  --mc-steps 100 --checkpoint-interval 10 --progress-interval 1\
  --temperatures 298,573,623,673,773 --use-ray --output ./output_test --rng 42 2>&1 | tee file.log