import shutil
from tests import FlexGetBase, with_filecopy


class TestTorrentSize(FlexGetBase):

    __yaml__ = """
        feeds:
          test_min:
            mock:
              - {title: 'test', file: 'tests/test_min.torrent'}
            accept_all: yes
            content_size:
              min: 2000

          test_max:
            mock:
              - {title: 'test', file: 'tests/test_max.torrent'}
            accept_all: yes
            content_size:
              max: 10

          test_strict:
            mock:
              - {title: 'test'}
            accept_all: yes
            content_size:
              min: 1
              strict: yes

          test_cache:
            mock:
              - {title: 'test', url: 'http://localhost/', file: 'tests/test.torrent'}
            accept_all: yes
            content_size:
              min: 2000
    """

    @with_filecopy('tests/test.torrent', 'tests/test_min.torrent')
    def test_min(self):
        """Content Size: torrent with min size"""
        self.execute_feed('test_min')
        assert self.feed.find_entry('rejected', title='test'), \
            'should have rejected, minimum size'

    @with_filecopy('tests/test.torrent', 'tests/test_max.torrent')
    def test_max(self):
        """Content Size: torrent with max size"""
        self.execute_feed('test_max')
        assert self.feed.find_entry('rejected', title='test'), \
            'should have rejected, maximum size'

    @with_filecopy('tests/test.torrent', 'tests/test_strict.torrent')
    def test_strict(self):
        """Content Size: strict enabled"""
        self.execute_feed('test_strict')
        assert self.feed.find_entry('rejected', title='test'), \
            'should have rejected non torrent'

    def test_cache(self):
        """Content Size: caching"""
        self.execute_feed('test_cache')
        assert self.feed.find_entry('rejected', title='test'), \
            'should have rejected, too small'

        # Remove the torrent from the mock entry and make sure it is still rejected
        del self.manager.config['feeds']['test_cache']['mock'][0]['file']
        self.execute_feed('test_cache')
        assert self.feed.find_entry('rejected', title='test'), \
            'should have rejected, size present from the cache'


class TestFileSize(FlexGetBase):
    """This is to test that content_size is picked up from the file itself when listdir is used as the input.
    This doesn't do a super job of testing, because we don't have any test files bigger than 1 MB."""

    __yaml__ = """
        feeds:
          test_min:
            mock:
              - {title: 'test', location: 'tests/min.file'}
            accept_all: yes
            content_size:
              min: 2000

          test_max:
            mock:
              - {title: 'test', location: 'tests/max.file'}
            accept_all: yes
            content_size:
              max: 2000

          test_torrent:
            mock:
              # content_size should not be read for this directly, as it is a torrent file
              - {title: 'test', location: 'tests/test.torrent'}
    """

    @with_filecopy('tests/test.torrent', 'tests/min.file')
    def test_min(self):
        """Content Size: torrent with min size"""
        self.execute_feed('test_min')
        entry = self.feed.find_entry('rejected', title='test')
        assert entry, 'should have rejected, minimum size'
        assert entry['content_size'] == 0, \
            'content_size was not detected'

    @with_filecopy('tests/test.torrent', 'tests/max.file')
    def test_max(self):
        """Content Size: torrent with max size"""
        self.execute_feed('test_max')
        entry = self.feed.find_entry('accepted', title='test')
        assert entry, 'should have been accepted, it is below maximum size'
        assert entry['content_size'] == 0, \
            'content_size was not detected'

    def test_torrent(self):
        self.execute_feed('test_torrent')
        entry = self.feed.find_entry('entries', title='test')
        assert 'content_size' not in entry, \
            'size of .torrent file should not be read as content_size'
