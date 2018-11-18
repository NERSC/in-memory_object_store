#https://arrow.apache.org/blog/

import pickle
import pyarrow
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import numpy as np
import timeit
import sys
import copy
from pympler import asizeof
def benchmark_object(obj, number=10):
    # Time serialization and deserialization for pickle.
    pickle_serialize = timeit.timeit(
        lambda: pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL),
        number=number)
    serialized_obj = pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)
    pickle_deserialize = timeit.timeit(lambda: pickle.loads(serialized_obj),
                                       number=number)

    # Time serialization and deserialization for Ray.
    ray_serialize = timeit.timeit(
        lambda: pyarrow.serialize(obj).to_buffer(), number=number)
    serialized_obj = pyarrow.serialize(obj).to_buffer()
    ray_deserialize = timeit.timeit(
        lambda: pyarrow.deserialize(serialized_obj), number=number)

    return [[pickle_serialize, pickle_deserialize],
            [ray_serialize, ray_deserialize]]


def plot(pickle_times, ray_times, title, i):
    fig, ax = plt.subplots()
    fig.set_size_inches(3.8, 2.7)

    bar_width = 0.35
    index = np.arange(2)
    opacity = 0.6

    plt.bar(index, pickle_times, bar_width,
            alpha=opacity, color='r', label='Pickle')

    plt.bar(index + bar_width, ray_times, bar_width,
            alpha=opacity, color='c', label='Plasma')
    print ('speedup: serialize:%f,deserialize:%f'%(pickle_times[0]/ray_times[0],pickle_times[1]/ray_times[1]))
    plt.title(title, fontweight='bold')
    plt.ylabel('Time (seconds)', fontsize=10)
    labels = ['serialization', 'deserialization']
    plt.xticks(index + bar_width / 2, labels, fontsize=10)
    plt.legend(fontsize=10, bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.yticks(fontsize=10)
    plt.savefig('plot-' + str(i) + '.png', format='png')


test_objects = [
    [np.random.randn(50000) for i in range(100)],
    {'weight-' + str(i): np.random.randn(50000) for i in range(100)},
    {i: set(['string1' + str(i), 'string2' + str(i)]) for i in range(100000)},
    [str(i) for i in range(200000)]
]

titles = [
    'List of large numpy arrays',
    'Dictionary of large numpy arrays',
    'Large dictionary of small sets',
    'Large list of strings'
]

for i in range(len(test_objects)):
    plot(*benchmark_object(test_objects[i]), titles[i], i)
    x=copy.deepcopy(test_objects[i])
    print (titles[i],asizeof.asizeof(x))
