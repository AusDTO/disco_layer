from distutils.core import setup
from gitdiscribe import Gitdiscribe

gd = Gitdiscribe('.')
if gd.tag != '':
  VERSION = gd.tag_number
  gd.write_version_file()
else:
    from version import VERSION

setup(
    name = 'AusDTODiscoService',
     version = VERSION,
     description = 'Making Australian government discoverable',
     long_description='''Making Australian government discoverable.

See Pia's post here https://www.dto.gov.au/blog/making-government-discoverable''',
      url='https://github.com/AusDTO/discoveryLayer',
      author='Digital Transformation Office',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Topic :: Internet :: WWW/HTTP :: Indexing/Search'],
      license='GPLv3',
)
