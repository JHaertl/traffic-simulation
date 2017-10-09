from setuptools import setup
import io
import simulation


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


setup(name='traffic-simulation',
      version=simulation.__version__,
      url='https://github.com/JHaertl/traffic-simulation',
      description='Agent based traffic simulation',
      long_description=read('README.md'),
      platforms='any',
      author='Jonathan Härtl',
      author_email='jonathan.haertl@gmx.de',
      packages=['simulation', 'simulation.agent', 'simulation.io',
                'simulation.layout', 'simulation.test', 'simulation.examples'],
      python_requires='>=3',
      install_requires=['numpy', 'opencv-python'],
      classifiers=[
          'Programming Language :: Python',
          'Natural Language :: English',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Operating System :: OS Independent',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Scientific/Engineering :: Artificial Intelligence']
      )
