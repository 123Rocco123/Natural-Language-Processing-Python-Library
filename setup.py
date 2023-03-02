from setuptools import setup, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Science/Research',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

setup(
  name='ptrNaturalLanguage',
  version='0.0.2',
  description='Natural Language Processing Library',
  #long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',
  author='Rocco Pio Maria Petruccio',
  author_email='whatsappbackuprocco@gmail.com',
  license='MIT',
  classifiers=classifiers,
  keywords=["Artificial Intelligence", "Natural Language Processing", "bs4", "requests", "requests_html"],
  packages=find_packages(),
  install_requires=[]
)
