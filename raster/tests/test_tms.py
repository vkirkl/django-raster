import inspect
import os
import shutil

from django.core.files import File
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from django.test.utils import override_settings
from raster.models import Legend, LegendEntry, LegendSemantics, RasterLayer


@override_settings(RASTER_TILE_CACHE_TIMEOUT=0)
class RasterTmsTests(TestCase):

    def setUp(self):
        # Instantiate Django file instances with nodes and links
        self.pwd = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe())))

        sourcefile = File(open(os.path.join(self.pwd, 'raster.tif.zip')))

        # Create legend
        sem1 = LegendSemantics.objects.create(name='Earth')
        ent1 = LegendEntry.objects.create(semantics=sem1, expression='4', color='#123456')
        leg = Legend.objects.create(title='MyLegend')
        leg.entries.add(ent1)

        # Create raster layer
        self.rasterlayer = RasterLayer.objects.create(
            name='Raster data',
            description='Small raster for testing',
            datatype='ca',
            srid='3086',
            nodata='0',
            rasterfile=sourcefile,
            legend=leg
        )

        self.tile = self.rasterlayer.rastertile_set.get(tilez=11, tilex=552, tiley=858)
        self.tile_url = reverse('tms', kwargs={'z': self.tile.tilez, 'y': self.tile.tiley, 'x': self.tile.tilex, 'layer': 'raster.tif', 'format': '.png'})

        self.client = Client()

    def tearDown(self):
        shutil.rmtree(os.path.dirname(os.path.join(
            self.pwd, '../..', self.rasterlayer.rasterfile.name)))
        self.rasterlayer.rastertile_set.all().delete()

    def test_tms_nonexisting_layer(self):
        url = reverse('tms', kwargs={'z': 0, 'y': 0, 'x': 0, 'layer': 'raster_nonexistent.tif', 'format': '.png'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_tms_nonexisting_tile(self):
        url = reverse('tms', kwargs={'z': 100, 'y': 0, 'x': 0, 'layer': 'raster.tif', 'format': '.png'})
        response = self.client.get(url)
        self.assertEqual(response['Content-type'], 'PNG')
        self.assertEqual(response.content, '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x00\x00\x00\x01\x00\x08\x06\x00\x00\x00\\r\xa8f\x00\x00\x01\x15IDATx\x9c\xed\xc11\x01\x00\x00\x00\xc2\xa0\xf5O\xedk\x08\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00x\x03\x01<\x00\x01<\xedS\t\x00\x00\x00\x00IEND\xaeB`\x82')

    def test_tms_existing_tile(self):
        leg = self.rasterlayer.legend
        self.rasterlayer.legend = None
        self.rasterlayer.save()

        # Get tms tile for layer without legend
        response = self.client.get(self.tile_url)
        self.assertEqual(response['Content-type'], 'PNG')
        self.assertEqual(response.content, '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x00\x00\x00\x01\x00\x08\x06\x00\x00\x00\\r\xa8f\x00\x00\x01\x15IDATx\x9c\xed\xc11\x01\x00\x00\x00\xc2\xa0\xf5O\xedk\x08\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00x\x03\x01<\x00\x01<\xedS\t\x00\x00\x00\x00IEND\xaeB`\x82')

        self.rasterlayer.legend = leg
        self.rasterlayer.save()

        # Get tms tile rendered with legend
        response = self.client.get(self.tile_url)
        self.assertEqual(response['Content-type'], 'PNG')
        self.assertEqual(
            response.content,
            '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x00\x00\x00\x01\x00\x08\x06\x00\x00\x00\\r\xa8f\x00\x00\x06PIDATx\x9c\xed\xdd\xd9\x91\xdc6\x10\x00P\xca\xe5\x086\x16\xc5\xa2 \x15\x8bbQ\n\xf2\xd7\x94i\x9a\x07H\x02$\xd0\xfd\xde\x97K;\x1a\xc2[B\xa3\x1b\xc41M\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00]\xf9\xf6v\x03\xa0\xa6\xaf\xef?\xfel\xfd\xec\xf7\xaf\x9f\x8f\xfc{\xdfk\xc3U\xad\xda\xfeW\x8b/\x05\xc6\xf0\xf7\xdb\r\x80\'\xdc\x1dA?\xa3\xfa\xfc{\xbe\xbe\xff\xf83JV\xf1i\xe7\xf2{\x04\x00B\xab\xddA\xf7:}\x8b\xd4\xbf5%\x00$&\x03 \x84\xa7F\xdf\xdf\xbf~~\x9b?k\xad4\x18\x89\x00@X\xb5:\xe5V\xda\xbf\x9c\x0f\xa8\xf1\xacRk\xed\x99\xb7a\x19\xa8\xb6(\x01 1\x01\x00N\xf8d\x03\xf3Y\xf5\'\xdf\x06\xcc\xdb\xb1\x1c\xe1\xafd$\x02\x00\x1c(\x99\xf5\x1f\xf1\r\xc04\t\x00\x90\x9aI@\xc2\xaa\x99\x9a\xcfg\xfbG\x1d\xed\xd7\x0c\xf9\xea\x02\xe6\xb6j\xe1e\x00X\xce\x92o\xfd\xd9\xda\xf7\xbf9\xe3\xbf\xe6(\xb0\x99\x03\x00\x0e)\x01\x08k\x9e\xaeo\x8d\x98{k\xfb\xb7\xd6\xff\xb7k\xf1}G\xed[\xfe\x1e\x04\x00\xc2)\xe9\xb8k\x9f\x89\xb4\xc6\xbf\x94\x12\x00\x12\x93\x01\x90\xcer\xa4/\xd9\xea\xdbS\x16Ps\xd1\x91\x00@hk\x9dx\xd9\xb9k\xcd\xa8\xaf=\xb7f\xe0h\xb1\xdaP\t\x00\x89\xc9\x00\x08gk&\x7f\xb9~\x7f\xed\xf3\xd9\x08\x00\xa4\xb3\xd7\xe1k\xad\xef\xefi\xce`\x8f\x12\x00\x12\x13\x00\x18\xd6\xda\x96\xd8\xbd\xcf\x96|\xeeS*\x9c-\x0bF-#\x94\x00\x84s\xd4\xd9\xf7\xea\xff\xab\xa9\xfb[)\xff\xdd\xe7\xca\x00 1\x19\x00\xe1\x1c\xa5\xe3w\xce\xf6\x8f\xb6\x1dX\x00 \x84\xb5\x857%\x9d\xbb\xb4\xf3\xaf-\x1cz2\x10\xd4*U\x96\x94\x00\x90\x98\x0c\x80\x10\xce\x9e\xd5\xbf\xf5\x99\xa3\xe3\xb6#\xa5\xff\xd3\xe4D \x06V\xd2\x19\xef\xbc\x9e\xeb\xa1\xb3\xb7\xde\xa2\xac\x04\x80\xc4\x94\x00\xa4pv\xed\x7f\x0f\xa3\xff\x96\x9am\x13\x00\x18R\xeb\xf4\xbf\xb5\xd2\xfd\x08\xad)\x01 1\x19\x00a]\x19I{K\xfd[\xdf>,\x00\x10\xce\xd6\xbd\x00\xb5\xbe\xfbN\xa7<\x1b`\xb6n%.\xbd\xcf\xe0\xe8\xfb\x95\x00\x90\x98\x0c\x80p\xae\x8e\xd0%#f\xad\x12\xa1f\xa9q\'#\x11\x00\x18V\xed{\xff\x9et\xf7-@\xad\xfd\x08J\x00HL\x06\xc0\xb0\xd6F\xbf\x16i\xff\xde\xdf\xbd\x9a\x85\xb4\x98\xa0\xbcr\xd0\xa9\x00\xc0\xf0JW\xf6\xbd\xb50\xe8\xea\xdc\xc2\x13\xfb\x18\x94\x00\x90X\xb7K%a\xcfr\x84{k\xd7\xdf\x9d\xeb\xc3\xb6&\xf2\x9e,c\x94\x00\x0ce\xeb\x1f\xfb\xd1\x8d\xc0=\xee\x0b\xe8a\xd5\xa1\x12\x00\x12\xeb.*\xc2\x9e\xadQ\xb3\xc6\x08\xdf\xc3\x88<M\xcf\x96\x00\x02\x00C\xa9\xb1\x96\xbeUG/Y\x93\x7fv\x01O\xed\xb9\x8d\xe5\xf7)\x01 1\x01\x80\xb0z\x9c\xf8\xfb\xe8\xa5m\xde\x02\x10N\xeb\x834K\x1c\xbd\xadh\xf1\xac\xbd\x13\x8e\xb7\x9e+\x03\x80\xc4d\x00\x0c\xefn:\xfd\xc6M?{my\xb2\x1d\x02\x00\xc3\xbb\xbb\xce\xff\x8d+\xbej\x95\x08w/-Q\x02@b2\x00\x86\xd7\xcb\x8c\xfa\x1dW\xcb\x90\xb3%\xc3\xf2\xb3\x02\x00\xc3:\x9a\xed\xbf\xb3Q\xe7\x8e\xbdgm-\xce9j_\xab\xed\xccJ\x00HL\x06@\x08k#\xe8\x9b\x87\x80\x94(I\xfb\xcf\xdez|\x96\x00\xc0\x90\xb6:A\x8b\x0e_ZJ\xdc\x99\xc1\x9f?\xab\xf5e sJ\x00HL\x06@\x08-v\xfd\x95d\x19\xb5\'\x17\x9f.[\x04\x00\x86\xd1{M\x7fV\x0f\xff/J\x00HL\x06@(-\xae\xdc\x9a\xa6\xb2\xb4\xbf\xa7=\x05\xa5\x04\x00\x86\xf4t\'\xabuo`\x0fi\xff\x9c\x12\x00\x12\x93\x010\xbc\x1e\x0e\x00\x19\x95\x0c\x80!\x1d\xdd\xae;_LS\xeb\xbc\x80\x1a>m\xeb%8\t\x00\x90\x98\x12\x80a\xec\x9dy\xd7R/\xa3u\x0b]\xcdHB\r=w\xd8ZA\xab\xd6}\x86J\x00HL\x00`(=M\xa0E`\x0e\x00fz[\xcdW\xfb\x86\xe3\xe5\xe9C2\x00HL\x00\x80D\x1c\nJ8\xad6\x00\xbd\xa5\xe4V\xdfZd\x00\x90\x98\x0c\x80!E;\x1c\xe4H\xab\xccD\x06\xc0Pj\xac\xed\xe7_\x02\x00$&\x000<\x19\xc1u\xe6\x00\x18\xd6\x93\xe7\xe7\xb7\xf0\xd4\x1b\x87\xe5\xef\xc7B `\x9a&\x19\x00A\xb4\xb8\x17 \x03\x01\x80pt\xfcrJ\x00HL\x06\xc0\x90\x96\xbb\xda\x96?\xfb\xfcw\xe6l\xa0drT\x00`xw\xb7\xcc\xbe\xb5\x05\xb8\x87\xd3\x8c\x95\x00\x90\x98\x0c\x80\xd0\x8e\xca\x81\xf9\xcf\xf7\xde\x97G%\x000\xbcQ\x17\x02\xcd\x9d\t6{\xf3\x1fg\x9f\xa3\x04\x80\xc4\x86\x8f\x9cpV\xe9V\xe2\xd6%@\xcb\xb7\x15\xa5\xe5\x8c\x00\xc0\xf0J\xdf\x02\x94\xec\x1dx\xb2\xee\xf7\x16\x00x\x95I@\xd2\x880YX\x9b\x00@\x08g:\xf72\xc5n\x11\x18J^?\x9e]\xc0TR2l-j\xdaj\x8f\x12\x00\x12\x93\x01\x10\xc2\x99\xc3AJ\xf6\x11\\\x99\x88\xbb\x93\x85\xbcEMD\x08g\xd3\xe9\x92\xcf\xbf\xf5F\xa0\xc5s\x95\x00\xc0\xff\x08\x00\x84s\xf6\x06\xe1\xcc7\x0e+\x01\x08\xe5N)\xf0\xa6\xb7\xce0\x90\x01@b\xde\x02\x10\xceH#\xff\xc7[G\x9c+\x01\x08\xa5d\x91Oo\x9d\x7f\x9a\xde;\x95H\t\x00\x89\t\x00\x84\x12y\xbd\x7f\x8b\x8bQ\xc3\xfe\xb2\xc8\xab\xb7E>=\x93\x01@b2\x00\xc29:\xfc\xf3\xe8\xb3\xd1\xcd\x7f\x172\x00\xc2iQ+G\xf4\xf5\xfd\xc7\x1f\x01\x00\x12\x13\x00H!c\xaa_B\x00 \xac\xb5\x93q\x05\x82\xff\x12\x00 1\x01\x80\xd0\xe6\x13\x82k\x93\x83\xd9\'\x0bm\x06"\xbd\x88A\xa0\xb4\xd4\x91\x01@b2\x00R\x98\x1f\x04\xda\xdbv\xe1e\xdb\x1c\x08\x02\x14\xbb\xb3\xf0I\x00\x80\xc4\x04\x00\xd2\xf8\x8c\x94\xbd\xad\x05\x98\xb7\xe7N\xdb\xaed\x01\x02\x00)\x1d-\n\x8a\xf8f`\x8d\x00\x00\x89\xa5\x88r\xb0t\xe6\xf8\xf0\'J\x86\xb5c\xc1[\x1d\x15>?\x7f\xf0\x1f\x1f\xce\xc8\x1aQZZ\x90\x00\x00\x00\x00IEND\xaeB`\x82'
        )

    def test_tms_legend_query_arg(self):
        sem2 = LegendSemantics.objects.create(name='Water')
        ent2 = LegendEntry.objects.create(semantics=sem2, expression='4', color='#654321')
        leg2 = Legend.objects.create(title='Other')
        leg2.entries.add(ent2)
        response = self.client.get(self.tile_url + '?legend=other')
        self.assertEqual(response['Content-type'], 'PNG')
        self.assertEqual(
            response.content,
            '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x00\x00\x00\x01\x00\x08\x06\x00\x00\x00\\r\xa8f\x00\x00\x06PIDATx\x9c\xed\xdd\xd9\x91\xdc6\x10\x00P\xca\xe5D6\x16\xc5\xa2\xa8\x14\x8bbQ(\xf2\xd7\x94i\x9a\x07H\x02$\xd0\xfd\xde\x97K;\x1a\xc2[B\xa3\x1b\xc41M\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00]\xf9\xf6v\x03\xa0\xa6\x1f\xdf\xbf\xfel\xfd\xec\xe7\xaf\xdf\x8f\xfc{\xdfk\xc3U\xad\xda\xfeW\x8b/\x05\xc6\xf0\xf7\xdb\r\x80\'\xdc\x1dA?\xa3\xfa\xfc{~|\xff\xfa3JV\xf1i\xe7\xf2{\x04\x00B\xab\xddA\xf7:}\x8b\xd4\xbf5%\x00$&\x03 \x84\xa7F\xdf\x9f\xbf~\x7f\x9b?k\xad4\x18\x89\x00@X\xb5:\xe5V\xda\xbf\x9c\x0f\xa8\xf1\xacRk\xed\x99\xb7a\x19\xa8\xb6(\x01 1\x01\x00N\xf8d\x03\xf3Y\xf5\'\xdf\x06\xcc\xdb\xb1\x1c\xe1\xafd$\x02\x00\x1c(\x99\xf5\x1f\xf1\r\xc04\t\x00\x90\x9aI@\xc2\xaa\x99\x9a\xcfg\xfbG\x1d\xed\xd7\x0c\xf9\xea\x02\xe6\xb6j\xe1e\x00X\xce\x92o\xfd\xd9\xda\xf7\xbf9\xe3\xbf\xe6(\xb0\x99\x03\x00\x0e)\x01\x08k\x9e\xaeo\x8d\x98{k\xfb\xb7\xd6\xff\xb7k\xf1}G\xed[\xfe\x1e\x04\x00\xc2)\xe9\xb8k\x9f\x89\xb4\xc6\xbf\x94\x12\x00\x12\x93\x01\x90\xcer\xa4/\xd9\xea\xdbS\x16Ps\xd1\x91\x00@hk\x9dx\xd9\xb9k\xcd\xa8\xaf=\xb7f\xe0h\xb1\xdaP\t\x00\x89\xc9\x00\x08gk&\x7f\xb9~\x7f\xed\xf3\xd9\x08\x00\xa4\xb3\xd7\xe1k\xad\xef\xefi\xce`\x8f\x12\x00\x12\x13\x00\x18\xd6\xda\x96\xd8\xbd\xcf\x96|\xeeS*\x9c-\x0bF-#\x94\x00\x84s\xd4\xd9\xf7\xea\xff\xab\xa9\xfb[)\xff\xdd\xe7\xca\x00 1\x19\x00\xe1\x1c\xa5\xe3w\xce\xf6\x8f\xb6\x1dX\x00 \x84\xb5\x857%\x9d\xbb\xb4\xf3\xaf-\x1cz2\x10\xd4*U\x96\x94\x00\x90\x98\x0c\x80\x10\xce\x9e\xd5\xbf\xf5\x99\xa3\xe3\xb6#\xa5\xff\xd3\xe4D \x06V\xd2\x19\xef\xbc\x9e\xeb\xa1\xb3\xb7\xde\xa2\xac\x04\x80\xc4\x94\x00\xa4pv\xed\x7f\x0f\xa3\xff\x96\x9am\x13\x00\x18R\xeb\xf4\xbf\xb5\xd2\xfd\x08\xad)\x01 1\x19\x00a]\x19I{K\xfd[\xdf>,\x00\x10\xce\xd6\xbd\x00\xb5\xbe\xfbN\xa7<\x1b`\xb6n%.\xbd\xcf\xe0\xe8\xfb\x95\x00\x90\x98\x0c\x80p\xae\x8e\xd0%#f\xad\x12\xa1f\xa9q\'#\x11\x00\x18V\xed{\xff\x9et\xf7-@\xad\xfd\x08J\x00HL\x06\xc0\xb0\xd6F\xbf\x16i\xff\xde\xdf\xbd\x9a\x85\xb4\x98\xa0\xbcr\xd0\xa9\x00\xc0\xf0JW\xf6\xbd\xb50\xe8\xea\xdc\xc2\x13\xfb\x18\x94\x00\x90X\xb7K%a\xcfr\x84{k\xd7\xdf\x9d\xeb\xc3\xb6&\xf2\x9e,c\x94\x00\x0ce\xeb\x1f\xfb\xd1\x8d\xc0=\xee\x0b\xe8a\xd5\xa1\x12\x00\x12\xeb.*\xc2\x9e\xadQ\xb3\xc6\x08\xdf\xc3\x88<M\xcf\x96\x00\x02\x00C\xa9\xb1\x96\xbeUG/Y\x93\x7fv\x01O\xed\xb9\x8d\xe5\xf7)\x01 1\x01\x80\xb0z\x9c\xf8\xfb\xe8\xa5m\xde\x02\x10N\xeb\x834K\x1c\xbd\xadh\xf1\xac\xbd\x13\x8e\xb7\x9e+\x03\x80\xc4d\x00\x0c\xefn:\xfd\xc6M?{my\xb2\x1d\x02\x00\xc3\xbb\xbb\xce\xff\x8d+\xbej\x95\x08w/-Q\x02@b2\x00\x86\xd7\xcb\x8c\xfa\x1dW\xcb\x90\xb3%\xc3\xf2\xb3\x02\x00\xc3:\x9a\xed\xbf\xb3Q\xe7\x8e\xbdgm-\xce9j_\xab\xed\xccJ\x00HL\x06@\x08k#\xe8\x9b\x87\x80\x94(I\xfb\xcf\xdez|\x96\x00\xc0\x90\xb6:A\x8b\x0e_ZJ\xdc\x99\xc1\x9f?\xab\xf5e sJ\x00HL\x06@\x08-v\xfd\x95d\x19\xb5\'\x17\x9f.[\x04\x00\x86\xd1{M\x7fV\x0f\xff/J\x00HL\x06@(-\xae\xdc\x9a\xa6\xb2\xb4\xbf\xa7=\x05\xa5\x04\x00\x86\xf4t\'\xabuo`\x0fi\xff\x9c\x12\x00\x12\x93\x010\xbc\x1e\x0e\x00\x19\x95\x0c\x80!\x1d\xdd\xae;_LS\xeb\xbc\x80\x1a>m\xeb%8\t\x00\x90\x98\x12\x80a\xec\x9dy\xd7R/\xa3u\x0b]\xcdHB\r=w\xd8ZA\xab\xd6}\x86J\x00HL\x00`(=M\xa0E`\x0e\x00fz[\xcdW\xfb\x86\xe3\xe5\xe9C2\x00HL\x00\x80D\x1c\nJ8\xad6\x00\xbd\xa5\xe4V\xdfZd\x00\x90\x98\x0c\x80!E;\x1c\xe4H\xab\xccD\x06\xc0Pj\xac\xed\xe7_\x02\x00$&\x000<\x19\xc1u\xe6\x00\x18\xd6\x93\xe7\xe7\xb7\xf0\xd4\x1b\x87\xe5\xef\xc7B `\x9a&\x19\x00A\xb4\xb8\x17 \x03\x01\x80pt\xfcrJ\x00HL\x06\xc0\x90\x96\xbb\xda\x96?\xfb\xfcw\xe6l\xa0drT\x00`xw\xb7\xcc\xbe\xb5\x05\xb8\x87\xd3\x8c\x95\x00\x90\x98\x0c\x80\xd0\x8e\xca\x81\xf9\xcf\xf7\xde\x97G%\x000\xbcQ\x17\x02\xcd\x9d\t6{\xf3\x1fg\x9f\xa3\x04\x80\xc4\x86\x8f\x9cpV\xe9V\xe2\xd6%@\xcb\xb7\x15\xa5\xe5\x8c\x00\xc0\xf0J\xdf\x02\x94\xec\x1dx\xb2\xee\xf7\x16\x00x\x95I@\xd2\x880YX\x9b\x00@\x08g:\xf72\xc5n\x11\x18J^?\x9e]\xc0TR2l-j\xdaj\x8f\x12\x00\x12\x93\x01\x10\xc2\x99\xc3AJ\xf6\x11\\\x99\x88\xbb\x93\x85\xbcEMD\x08g\xd3\xe9\x92\xcf\xbf\xf5F\xa0\xc5s\x95\x00\xc0\xff\x08\x00\x84s\xf6\x06\xe1\xcc7\x0e+\x01\x08\xe5N)\xf0\xa6\xb7\xce0\x90\x01@b\xde\x02\x10\xceH#\xff\xc7[G\x9c+\x01\x08\xa5d\x91Oo\x9d\x7f\x9a\xde;\x95H\t\x00\x89\t\x00\x84\x12y\xbd\x7f\x8b\x8bQ\xc3\xfe\xb2\xc8\xab\xb7E>=\x93\x01@b2\x00\xc29:\xfc\xf3\xe8\xb3\xd1\xcd\x7f\x172\x00\xc2iQ+G\xf4\xe3\xfb\xd7\x1f\x01\x00\x12\x13\x00H!c\xaa_B\x00 \xac\xb5\x93q\x05\x82\xff\x12\x00 1\x01\x80\xd0\xe6\x13\x82k\x93\x83\xd9\'\x0bm\x06"\xbd\x88A\xa0\xb4\xd4\x91\x01@b2\x00R\x98\x1f\x04\xda\xdbv\xe1e\xdb\x1c\x08\x02\x14\xbb\xb3\xf0I\x00\x80\xc4\x04\x00\xd2\xf8\x8c\x94\xbd\xad\x05\x98\xb7\xe7N\xdb\xaed\x01\x02\x00)\x1d-\n\x8a\xf8f`\x8d\x00\x00\x89\xa5\x88r\xb0t\xe6\xf8\xf0\'J\x86\xb5c\xc1[\x1d\x15>?\x7f\xf0\x1f\xf3o\xcd3H\xfd"q\x00\x00\x00\x00IEND\xaeB`\x82'
        )

    def test_tms_entries_query_arg(self):
        # Create other legend
        sem2 = LegendSemantics.objects.create(name='Bla')
        ent2 = LegendEntry.objects.create(semantics=sem2, expression='4', color='#654321')
        ent3 = LegendEntry.objects.create(semantics=sem2, expression='5', color='#123456')
        leg2 = Legend.objects.create(title='Dual')
        leg2.entries.add(ent2, ent3)
        response = self.client.get(self.tile_url + '?entries=4&legend=dual')
        self.assertEqual(response['Content-type'], 'PNG')
        self.assertEqual(
            response.content,
            '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x00\x00\x00\x01\x00\x08\x06\x00\x00\x00\\r\xa8f\x00\x00\x06PIDATx\x9c\xed\xdd\xd9\x91\xdc6\x10\x00P\xca\xe5D6\x16\xc5\xa2\xa8\x14\x8bbQ(\xf2\xd7\x94i\x9a\x07H\x02$\xd0\xfd\xde\x97K;\x1a\xc2[B\xa3\x1b\xc41M\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00]\xf9\xf6v\x03\xa0\xa6\x1f\xdf\xbf\xfel\xfd\xec\xe7\xaf\xdf\x8f\xfc{\xdfk\xc3U\xad\xda\xfeW\x8b/\x05\xc6\xf0\xf7\xdb\r\x80\'\xdc\x1dA?\xa3\xfa\xfc{~|\xff\xfa3JV\xf1i\xe7\xf2{\x04\x00B\xab\xddA\xf7:}\x8b\xd4\xbf5%\x00$&\x03 \x84\xa7F\xdf\x9f\xbf~\x7f\x9b?k\xad4\x18\x89\x00@X\xb5:\xe5V\xda\xbf\x9c\x0f\xa8\xf1\xacRk\xed\x99\xb7a\x19\xa8\xb6(\x01 1\x01\x00N\xf8d\x03\xf3Y\xf5\'\xdf\x06\xcc\xdb\xb1\x1c\xe1\xafd$\x02\x00\x1c(\x99\xf5\x1f\xf1\r\xc04\t\x00\x90\x9aI@\xc2\xaa\x99\x9a\xcfg\xfbG\x1d\xed\xd7\x0c\xf9\xea\x02\xe6\xb6j\xe1e\x00X\xce\x92o\xfd\xd9\xda\xf7\xbf9\xe3\xbf\xe6(\xb0\x99\x03\x00\x0e)\x01\x08k\x9e\xaeo\x8d\x98{k\xfb\xb7\xd6\xff\xb7k\xf1}G\xed[\xfe\x1e\x04\x00\xc2)\xe9\xb8k\x9f\x89\xb4\xc6\xbf\x94\x12\x00\x12\x93\x01\x90\xcer\xa4/\xd9\xea\xdbS\x16Ps\xd1\x91\x00@hk\x9dx\xd9\xb9k\xcd\xa8\xaf=\xb7f\xe0h\xb1\xdaP\t\x00\x89\xc9\x00\x08gk&\x7f\xb9~\x7f\xed\xf3\xd9\x08\x00\xa4\xb3\xd7\xe1k\xad\xef\xefi\xce`\x8f\x12\x00\x12\x13\x00\x18\xd6\xda\x96\xd8\xbd\xcf\x96|\xeeS*\x9c-\x0bF-#\x94\x00\x84s\xd4\xd9\xf7\xea\xff\xab\xa9\xfb[)\xff\xdd\xe7\xca\x00 1\x19\x00\xe1\x1c\xa5\xe3w\xce\xf6\x8f\xb6\x1dX\x00 \x84\xb5\x857%\x9d\xbb\xb4\xf3\xaf-\x1cz2\x10\xd4*U\x96\x94\x00\x90\x98\x0c\x80\x10\xce\x9e\xd5\xbf\xf5\x99\xa3\xe3\xb6#\xa5\xff\xd3\xe4D \x06V\xd2\x19\xef\xbc\x9e\xeb\xa1\xb3\xb7\xde\xa2\xac\x04\x80\xc4\x94\x00\xa4pv\xed\x7f\x0f\xa3\xff\x96\x9am\x13\x00\x18R\xeb\xf4\xbf\xb5\xd2\xfd\x08\xad)\x01 1\x19\x00a]\x19I{K\xfd[\xdf>,\x00\x10\xce\xd6\xbd\x00\xb5\xbe\xfbN\xa7<\x1b`\xb6n%.\xbd\xcf\xe0\xe8\xfb\x95\x00\x90\x98\x0c\x80p\xae\x8e\xd0%#f\xad\x12\xa1f\xa9q\'#\x11\x00\x18V\xed{\xff\x9et\xf7-@\xad\xfd\x08J\x00HL\x06\xc0\xb0\xd6F\xbf\x16i\xff\xde\xdf\xbd\x9a\x85\xb4\x98\xa0\xbcr\xd0\xa9\x00\xc0\xf0JW\xf6\xbd\xb50\xe8\xea\xdc\xc2\x13\xfb\x18\x94\x00\x90X\xb7K%a\xcfr\x84{k\xd7\xdf\x9d\xeb\xc3\xb6&\xf2\x9e,c\x94\x00\x0ce\xeb\x1f\xfb\xd1\x8d\xc0=\xee\x0b\xe8a\xd5\xa1\x12\x00\x12\xeb.*\xc2\x9e\xadQ\xb3\xc6\x08\xdf\xc3\x88<M\xcf\x96\x00\x02\x00C\xa9\xb1\x96\xbeUG/Y\x93\x7fv\x01O\xed\xb9\x8d\xe5\xf7)\x01 1\x01\x80\xb0z\x9c\xf8\xfb\xe8\xa5m\xde\x02\x10N\xeb\x834K\x1c\xbd\xadh\xf1\xac\xbd\x13\x8e\xb7\x9e+\x03\x80\xc4d\x00\x0c\xefn:\xfd\xc6M?{my\xb2\x1d\x02\x00\xc3\xbb\xbb\xce\xff\x8d+\xbej\x95\x08w/-Q\x02@b2\x00\x86\xd7\xcb\x8c\xfa\x1dW\xcb\x90\xb3%\xc3\xf2\xb3\x02\x00\xc3:\x9a\xed\xbf\xb3Q\xe7\x8e\xbdgm-\xce9j_\xab\xed\xccJ\x00HL\x06@\x08k#\xe8\x9b\x87\x80\x94(I\xfb\xcf\xdez|\x96\x00\xc0\x90\xb6:A\x8b\x0e_ZJ\xdc\x99\xc1\x9f?\xab\xf5e sJ\x00HL\x06@\x08-v\xfd\x95d\x19\xb5\'\x17\x9f.[\x04\x00\x86\xd1{M\x7fV\x0f\xff/J\x00HL\x06@(-\xae\xdc\x9a\xa6\xb2\xb4\xbf\xa7=\x05\xa5\x04\x00\x86\xf4t\'\xabuo`\x0fi\xff\x9c\x12\x00\x12\x93\x010\xbc\x1e\x0e\x00\x19\x95\x0c\x80!\x1d\xdd\xae;_LS\xeb\xbc\x80\x1a>m\xeb%8\t\x00\x90\x98\x12\x80a\xec\x9dy\xd7R/\xa3u\x0b]\xcdHB\r=w\xd8ZA\xab\xd6}\x86J\x00HL\x00`(=M\xa0E`\x0e\x00fz[\xcdW\xfb\x86\xe3\xe5\xe9C2\x00HL\x00\x80D\x1c\nJ8\xad6\x00\xbd\xa5\xe4V\xdfZd\x00\x90\x98\x0c\x80!E;\x1c\xe4H\xab\xccD\x06\xc0Pj\xac\xed\xe7_\x02\x00$&\x000<\x19\xc1u\xe6\x00\x18\xd6\x93\xe7\xe7\xb7\xf0\xd4\x1b\x87\xe5\xef\xc7B `\x9a&\x19\x00A\xb4\xb8\x17 \x03\x01\x80pt\xfcrJ\x00HL\x06\xc0\x90\x96\xbb\xda\x96?\xfb\xfcw\xe6l\xa0drT\x00`xw\xb7\xcc\xbe\xb5\x05\xb8\x87\xd3\x8c\x95\x00\x90\x98\x0c\x80\xd0\x8e\xca\x81\xf9\xcf\xf7\xde\x97G%\x000\xbcQ\x17\x02\xcd\x9d\t6{\xf3\x1fg\x9f\xa3\x04\x80\xc4\x86\x8f\x9cpV\xe9V\xe2\xd6%@\xcb\xb7\x15\xa5\xe5\x8c\x00\xc0\xf0J\xdf\x02\x94\xec\x1dx\xb2\xee\xf7\x16\x00x\x95I@\xd2\x880YX\x9b\x00@\x08g:\xf72\xc5n\x11\x18J^?\x9e]\xc0TR2l-j\xdaj\x8f\x12\x00\x12\x93\x01\x10\xc2\x99\xc3AJ\xf6\x11\\\x99\x88\xbb\x93\x85\xbcEMD\x08g\xd3\xe9\x92\xcf\xbf\xf5F\xa0\xc5s\x95\x00\xc0\xff\x08\x00\x84s\xf6\x06\xe1\xcc7\x0e+\x01\x08\xe5N)\xf0\xa6\xb7\xce0\x90\x01@b\xde\x02\x10\xceH#\xff\xc7[G\x9c+\x01\x08\xa5d\x91Oo\x9d\x7f\x9a\xde;\x95H\t\x00\x89\t\x00\x84\x12y\xbd\x7f\x8b\x8bQ\xc3\xfe\xb2\xc8\xab\xb7E>=\x93\x01@b2\x00\xc29:\xfc\xf3\xe8\xb3\xd1\xcd\x7f\x172\x00\xc2iQ+G\xf4\xe3\xfb\xd7\x1f\x01\x00\x12\x13\x00H!c\xaa_B\x00 \xac\xb5\x93q\x05\x82\xff\x12\x00 1\x01\x80\xd0\xe6\x13\x82k\x93\x83\xd9\'\x0bm\x06"\xbd\x88A\xa0\xb4\xd4\x91\x01@b2\x00R\x98\x1f\x04\xda\xdbv\xe1e\xdb\x1c\x08\x02\x14\xbb\xb3\xf0I\x00\x80\xc4\x04\x00\xd2\xf8\x8c\x94\xbd\xad\x05\x98\xb7\xe7N\xdb\xaed\x01\x02\x00)\x1d-\n\x8a\xf8f`\x8d\x00\x00\x89\xa5\x88r\xb0t\xe6\xf8\xf0\'J\x86\xb5c\xc1[\x1d\x15>?\x7f\xf0\x1f\xf3o\xcd3H\xfd"q\x00\x00\x00\x00IEND\xaeB`\x82'
        )

    def test_tms_legend_url_from_layer_name(self):
        url = reverse('legend', kwargs={'layer_or_legend_name': 'raster.tif'})
        response = self.client.get(url)
        self.assertEqual(response.content, '[{"color": "#123456", "expression": "4", "name": "Earth"}]')

    def test_tms_legend_url_error(self):
        url = reverse('legend', kwargs={'layer_or_legend_name': 'raster_does_not_exist.tif'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_tms_legend_url_from_legend_name(self):
        url = reverse('legend', kwargs={'layer_or_legend_name': 'MyLegend'})
        response = self.client.get(url)
        self.assertEqual(response.content, '[{"color": "#123456", "expression": "4", "name": "Earth"}]')
