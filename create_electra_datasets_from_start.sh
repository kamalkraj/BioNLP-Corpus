# Download dataset
# Download baseline
python PubMedDownloader.py --dataset baseline --action download_extract --path data/raw --keep_extracted_only
# Download daily_update
python PubMedDownloader.py --dataset daily_update --action download_extract --path data/raw --keep_extracted_only

# Copy daily_update files to baseline
cp data/raw/daily_update/* data/raw/baseline

# Format dataset
python PubMedTextFormatting.py --dataset_path data/raw/baseline --output_filename data/formatted/pubmed_baseline_one_article_per_line.txt

# Sharding
python TextSharding.py --input_files data/formatted/pubmed_baseline_one_article_per_line.txt --segmenter scispacy --n_training_shards 2048 --n_test_shards 2048 --fraction_test_set 0.1