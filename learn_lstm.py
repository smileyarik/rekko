from __future__ import absolute_import, division, print_function

import tensorflow as tf

import sys
import numpy as np
import os
import time
from collections import defaultdict
import csv

def make_weeked_visits(vs, current_ts, pad):
    last_week = 1 + int(current_ts - vs[0][1])//(86400*7)
    seq = []
    seq.append(10200+last_week)
    for item,ts in vs:
        new_week = 1 + int(current_ts - ts)//(86400*7)
        while last_week > new_week:
            last_week -= 1
            seq.append(10200+last_week)
        seq.append(item)
    while last_week > 1:
        last_week -= 1
        seq.append(10200+last_week)
    while len(seq) < pad:
        seq.append(0)
    return seq

if __name__ == '__main__':
    tf.enable_eager_execution()

    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

    print("Reading transactions")
    user_visits = defaultdict(list)
    with open(sys.argv[1]) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        count = 0
        for row in reader:
            item = int(row[0])
            user = int(row[1])
            ts = int(float(row[3]) * 6)
            user_visits[user].append((item, ts))

    print("Making training set")
    for user in user_visits:
        user_visits[user] = sorted(user_visits[user], key=lambda x:x[1])

    current_ts = int(sys.argv[3]) * 6

    train_seqs = []
    valid_seqs = []
    max_seq = 0
    for user,visits in user_visits.iteritems():
        seq = make_weeked_visits(visits[-30:], current_ts, 60)
        if len(seq) > max_seq:
            max_seq = len(seq)
        if int(user) % 10 != 0:
            train_seqs.append(seq)
            if len(train_seqs) % 50000 == 1:
                print(seq)
        else:
            valid_seqs.append(seq)
    print(max_seq)

# The maximum length sentence we want for a single input in characters
    examples_per_epoch = len(train_seqs)

    train_dataset = tf.data.Dataset.from_tensor_slices(np.array(train_seqs))
    valid_dataset = tf.data.Dataset.from_tensor_slices(np.array(valid_seqs))

    def split_input_target(chunk):
        input_seq = chunk[:-1]
        target_seq = chunk[1:]
        return input_seq, target_seq

    train_sequences = train_dataset.map(split_input_target)
    valid_sequences = valid_dataset.map(split_input_target)

    BATCH_SIZE = 64
    steps_per_epoch = len(train_seqs)//BATCH_SIZE
    BUFFER_SIZE = 10000

    train_sequences = train_sequences.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)
    valid_sequences = valid_sequences.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)

    max_id = 0
    for user in user_visits:
        for item in user_visits[user]:
            max_id = max(max_id, item[0])

    print(max_id)
    vocab_size = max_id+30
    embedding_dim = 256
    rnn_units = 1024

    rnn = tf.keras.layers.CuDNNGRU

    checkpoint_dir = sys.argv[2]
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")

    checkpoint_callback=tf.keras.callbacks.ModelCheckpoint(
        filepath=checkpoint_prefix,
        save_weights_only=True)


    def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
        model = tf.keras.Sequential([
            tf.keras.layers.Embedding(vocab_size, embedding_dim,
                                  batch_input_shape=[batch_size, None]),
            rnn(rnn_units,
                return_sequences=True,
                recurrent_initializer='glorot_uniform',
                stateful=True),
            tf.keras.layers.Dense(vocab_size)
        ])
        return model

    def loss(labels, logits):
        return tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)

    model = build_model(
        vocab_size = vocab_size,
        embedding_dim=embedding_dim,
        rnn_units=rnn_units,
        batch_size=BATCH_SIZE)
    model.compile(
        optimizer = tf.train.AdamOptimizer(),
        loss = loss)

    print("Training model")
    history = model.fit(train_sequences.repeat(), epochs=3,
        steps_per_epoch=len(train_seqs)//BATCH_SIZE, callbacks=[checkpoint_callback],
        validation_data=valid_sequences.repeat(), validation_steps=len(valid_seqs)//BATCH_SIZE)

    print(tf.train.latest_checkpoint(checkpoint_dir))




