import unittest

from lbry.schema.url import URL


claim_id = "63f2da17b0d90042c559cc73b6b17f853945c43e"


class TestURLParsing(unittest.TestCase):

    segments = 'stream', 'channel'
    fields = 'name', 'claim_id', 'sequence', 'amount_order'

    def _assert_url(self, url_string, strictly=True, **kwargs):
        url = URL.parse(url_string)
        if strictly:
            if url_string.startswith('lbry://'):
                self.assertEqual(url_string, str(url))
            else:
                self.assertEqual(f'lbry://{url_string}', str(url))
        present = {}
        for key in kwargs:
            for segment_name in self.segments:
                if key.startswith(segment_name):
                    present[segment_name] = True
                    break
        for segment_name in self.segments:
            segment = getattr(url, segment_name)
            if segment_name not in present:
                self.assertIsNone(segment)
            else:
                for field in self.fields:
                    self.assertEqual(
                        getattr(segment, field),
                        kwargs.get(f'{segment_name}_{field}', None)
                    )

    def _fail_url(self, url):
        with self.assertRaisesRegex(ValueError, 'Invalid LBRY URL'):
            URL.parse(url)

    def test_parser_valid_urls(self):
        url = self._assert_url
        # stream
        url('test', stream_name='test')
        url('test*1', stream_name='test', stream_sequence='1')
        url('test$1', stream_name='test', stream_amount_order='1')
        url(f'test#{claim_id}', stream_name='test', stream_claim_id=claim_id, strictly=False)
        url(f'test:{claim_id}', stream_name='test', stream_claim_id=claim_id)
        # channel
        url('@test', channel_name='@test')
        url('@test*1', channel_name='@test', channel_sequence='1')
        url('@test$1', channel_name='@test', channel_amount_order='1')
        url(f'@test#{claim_id}', channel_name='@test', channel_claim_id=claim_id, strictly=False)
        url(f'@test:{claim_id}', channel_name='@test', channel_claim_id=claim_id)
        # channel/stream
        url('lbry://@test/stuff', channel_name='@test', stream_name='stuff')
        url('lbry://@test*1/stuff', channel_name='@test', channel_sequence='1', stream_name='stuff')
        url('lbry://@test$1/stuff', channel_name='@test', channel_amount_order='1', stream_name='stuff')
        url(f'lbry://@test#{claim_id}/stuff', channel_name='@test', channel_claim_id=claim_id, stream_name='stuff', strictly=False)
        url(f'lbry://@test:{claim_id}/stuff', channel_name='@test', channel_claim_id=claim_id, stream_name='stuff')
        # combined legacy and new
        url('@test:1/stuff#2', channel_claim_id='1', stream_claim_id='2', channel_name='@test', stream_name='stuff', strictly=False)
        url('@test*1/stuff#2', channel_sequence='1', stream_claim_id='2', channel_name='@test', stream_name='stuff', strictly=False)
        # unicode regex edges
        _url = lambda name: url(name, stream_name=name)
        _url('\uD799')
        _url('\uE000')
        _url('\uFFFD')

    def test_parser_invalid_urls(self):
        fail = self._fail_url
        fail("lbry://")
        fail("lbry://\u0000")
        fail("lbry://\u0008")
        fail("lbry://\u000b")
        fail("lbry://\u000c")
        fail("lbry://\u000e")
        fail("lbry://\u001f")
        fail("lbry://\uD800")
        fail("lbry://\uDFFF")
        fail("lbry://\uDFFE")
        fail("lbry://\uFFFF")
        fail("lbry://;")
        fail("lbry://no\ttab")
        fail("lbry://no space")
        fail("lbry://no\rcr")
        fail("lbry://no\new\nline")
        fail("lbry://\"")
        fail("lbry://\\")
        fail("lbry:///")
        fail("lbry://<") and fail("lbry://>")
        fail("lbry://{") and fail("lbry://}")
        fail("lbry://[") and fail("lbry://]")
        fail("lbry://%")
        fail("lbry://|")
        fail("lbry://^")
        fail("lbry://~")
        fail("lbry://`")
        fail("lbry://test:3$1")
        fail("lbry://test$1:1")
        fail("lbry://test#x")
        fail("lbry://test#x/page")
        fail("lbry://test$")
        fail("lbry://test#")
        fail("lbry://test:")
        fail("lbry://test$x")
        fail("lbry://test:x")
        fail("lbry://@test@")
        fail("lbry://@test:")
        fail("lbry://test@")
        fail("lbry://tes@t")
        fail(f"lbry://test:1#{claim_id}")
        fail("lbry://test*0")
        fail("lbry://test$0")
        fail("lbry://test/path")
        fail("lbry://@test1*1ab/fakepath")
        fail("lbry://test:1:1:1")
        fail("whatever/lbry://test")
        fail("lbry://lbry://test")
        fail("lbry://@/what")
        fail("lbry://abc:0x123")
        fail("lbry://abc:0x123/page")
        fail("lbry://@test1#ABCDEF/fakepath")
        fail("test*0001")
        fail("lbry://@test1$1/fakepath?arg1&arg2&arg3")
