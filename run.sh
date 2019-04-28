lstmver="003"
ver="003"

python split.py ../src_data/ratings.csv ../data/tr_st_ratings.csv ../data/tr_tg_ratings.csv ../data/vl_st_ratings.csv ../data/vl_tg_ratings.csv ../data/tt_st_ratings.csv 43441181 43873181 3
python split.py ../src_data/bookmarks.csv ../data/tr_st_bookmarks.csv ../data/tr_tg_bookmarks.csv ../data/vl_st_bookmarks.csv ../data/vl_tg_bookmarks.csv ../data/tt_st_bookmarks.csv 43441181 43873181 2
python split.py ../src_data/transactions.csv ../data/tr_st_transactions.csv ../data/tr_tg_transactions.csv ../data/vl_st_transactions.csv ../data/vl_tg_transactions.csv ../data/tt_st_transactions.csv 43441181 43873181 3

python make_profiles.py ../src_data/catalogue.json ../data/tr_st_transactions.csv ../data/tr_st_bookmarks.csv ../data/tr_st_ratings.csv ../src_data/test_users.json ../data/tr_user_pickle.bin ../data/tr_item_pickle.bin
python make_profiles.py ../src_data/catalogue.json ../data/vl_st_transactions.csv ../data/vl_st_bookmarks.csv ../data/vl_st_ratings.csv ../src_data/test_users.json ../data/vl_user_pickle.bin ../data/vl_item_pickle.bin
python make_profiles.py ../src_data/catalogue.json ../data/tt_st_transactions.csv ../data/tt_st_bookmarks.csv ../data/tt_st_ratings.csv ../src_data/test_users.json ../data/tt_user_pickle.bin ../data/tt_item_pickle.bin

export OPENBLAS_NUM_THREADS=1;
python learn_als.py ../data/tr_st_transactions.csv ../data/tr_user_als.bin ../data/tr_item_als.bin;
python learn_als.py ../data/vl_st_transactions.csv ../data/vl_user_als.bin ../data/vl_item_als.bin;
python learn_als.py ../data/tt_st_transactions.csv ../data/tt_user_als.bin ../data/tt_item_als.bin

python learn_lstm.py ../data/tt_st_transactions.csv ../data/tt_checkpoints_$lstmver 44305181 2> /dev/null
python learn_lstm.py ../data/tr_st_transactions.csv ../data/tr_checkpoints_$lstmver 43441181 2> /dev/null
python learn_lstm.py ../data/vl_st_transactions.csv ../data/vl_checkpoints_$lstmver 43873181 2> /dev/null

python make_features.py ../data/tr_user_pickle.bin ../data/tr_item_pickle.bin ../data/tr_user_als.bin ../data/tr_item_als.bin ../data/tr_tg_transactions.csv ../src_data/test_users.json ../data/tr_features_$ver.txt 43441181 ../data/tr_checkpoints_$lstmver
python make_features.py ../data/vl_user_pickle.bin ../data/vl_item_pickle.bin ../data/vl_user_als.bin ../data/vl_item_als.bin ../data/vl_tg_transactions.csv ../src_data/test_users.json ../data/vl_features_$ver.txt 43873181 ../data/vl_checkpoints_$lstmver
python make_features.py ../data/tt_user_pickle.bin ../data/tt_item_pickle.bin ../data/tt_user_als.bin ../data/tt_item_als.bin - ../src_data/test_users.json ../data/tt_features_$ver.txt 44305181 ../data/tt_checkpoints_$lstmver

cat ../data/vl_features_$ver.txt | awk -vOFS='\t' '{$1+=1000000;print $0}' > ../data/trvl_features_$ver.txt
cat ../data/tr_features_$ver.txt >> ../data/trvl_features_$ver.txt
catboost-gpu fit -f ../data/trvl_features_$ver.txt -m ../data/trvlmodel_$ver.bin --cd ../data/cd --loss-function YetiRank:decay=0.95 -i 4000 --learn-err-log ../data/trvllearn_error_$ver.txt --fstr-file ../data/trvlmodel_$ver.fstr --fstr-type FeatureImportance --fstr-internal-file ../data/trvlmodel_$ver.fstr_int --task-type GPU
catboost-gpu calc -m ../data/trvlmodel_$ver.bin --cd ../data/cd -o ../data/tt_output_$ver.txt --input-path ../data/tt_features_$ver.txt 2> ../data/apply_stderr.txt

cat ../data/tt_output_$ver.txt | awk 'NR>1' > ../data/a.txt;
cat ../data/tt_features_$ver.txt | awk -vOFS='\t' '{print $1,$2}' > ../data/b.txt
paste ../data/b.txt ../data/a.txt > ../data/c.txt

python make_result.py ../data/c.txt 3 > ../data/result_trvl_$ver.json

