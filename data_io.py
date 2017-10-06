from __future__ import print_function
import tensorflow as tf
import datetime
import config_reader
import os


class DataIO(object):

    def __init__(self, write: bool=True, path: str=None):
        self.write = write
        self.continous_write = False  # TODO: DONT FORGET THIS, ADD TO CONFIG?
        self.path = path
        self.read_sample_size = config_reader.CONFIG.getint('training', 'sample_size')
        self.write_sample_size = config_reader.CONFIG.getint('renderer', 'sample_size')
        self.data = []
        self.write_batch_size = 16  # has nothing to do with training batch sizes, just performs writes in chunks
        self.counter = 0
        if not self.write:
            return
        timestamp = '{:%Y-%m-%d_%H-%M}'.format(datetime.datetime.now())
        if path is None:
            self.save_dir = config_reader.CONFIG.get('renderer', 'save_dir')
            self.path = os.path.join(self.save_dir, 'data_' + timestamp + '.tfrecords')
        self.writer = tf.python_io.TFRecordWriter(self.path)

    def add_data(self, image):
        if not self.write:
            return
        self.data.append(image)
        if self.continous_write:
            if len(self.data) < 30:  # just an arbitrary buffer size sufficient for us atm
                return
            self._write_sample([self.data[0], self.data[4], self.data[8], self.data[12], self.data[16], self.data[20]])  # 0 4 8 chosen according to timestep/save_delay to get half second steps
            print('Wrote 1 sample. ' + str(self.counter) + ' total. Done.')
            self.data.pop(0)
        elif len(self.data) >= self.write_batch_size * self.write_sample_size:
            self._write_chunk(self.data)
            self.data = []

    def read_data(self, filename_queue, shape):
        reader = tf.TFRecordReader()
        _, serialized_example = reader.read(filename_queue)
        sample_dict = {}
        for i in range(self.read_sample_size):
            sample_dict['image' + str(i)] = tf.FixedLenFeature([], tf.string)
        features = tf.parse_single_example(serialized_example, features=sample_dict)
        images = []
        for i in range(self.read_sample_size):
            image = tf.decode_raw(features['image' + str(i)], tf.float32)
            image = tf.reshape(image, shape)
            images.append(image)
        return images

    def _write_sample(self, sample):
        if len(sample) != self.write_sample_size:
            print ("error, write called on unfinished sample data")
        sample_dict = {}
        for i in range(self.write_sample_size):
            sample_dict['image' + str(i)] = DataIO._bytes_feature(sample[i].tobytes())
        sample = tf.train.Example(features=tf.train.Features(feature=sample_dict))
        self.writer.write(sample.SerializeToString())
        self.counter += 1

    def _write_chunk(self, chunk):
        # currently writes each sample on its own. buffering needed
        if len(chunk) % self.write_sample_size != 0:
            print ("error, write called on unfinished sample data chunk")
        samples = len(chunk) / self.write_sample_size
        print('Writing ' + str(samples) + ' samples. ', end='')
        for s in range(samples):  # currently targets are not reused as inputs
            self._write_sample(chunk[(s * self.write_sample_size): (s * self.write_sample_size + self.write_sample_size)])
        print(str(self.counter) + ' total. Done')

    @staticmethod
    def _int64_feature(value):
        return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

    @staticmethod
    def _bytes_feature(value):
        return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))
