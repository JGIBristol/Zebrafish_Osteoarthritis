#!/bin/bash
# Shell script for training lots of models with the same configuration
# Useful in case we want to investigate the effect of the randomness in the training 
# process

# Backup the original config file
cp userconf.yml userconf.yml.backup

# This is where stuff will get saved to
mkdir -p logs/

for i in {0..19}; do
    echo "Training model attempt_${i}.pkl (iteration $((i+1)) of 19)"
    
    # Update the model_path in the YAML file
    sed -i "s/^model_path: .*/model_path: \"attempt_n${i}.pkl\"/" userconf.yml
    
    # Run the training script
    uv run python scripts/2-train_jaw_segmenter.py > "logs/attempt_${i}.log" 2>&1
    
    # Check if training was successful
    if [ $? -ne 0 ]; then
        echo "Training failed for attempt_${i}.pkl"
        # Restore original config and exit
        cp userconf.yml.backup userconf.yml
        exit 1
    fi
    
    echo "Completed training for attempt_${i}.pkl"
    echo "----------------------------------------"

    uv run python scripts/paper_scripts/compare_segmentations.py attempt_n${i}.pkl | tee "logs/attempt_${i}_inference.log" 2>&1
done

# Restore the original config file
cp userconf.yml.backup userconf.yml
rm userconf.yml.backup
