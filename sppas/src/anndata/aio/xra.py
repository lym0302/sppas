# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.anndata.aio.xra.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    SPPAS XRA reader and writer.

"""
import logging
from datetime import datetime
import xml.etree.cElementTree as ET

from sppas import encoding
from sppas.src.utils.makeunicode import u

from ..media import sppasMedia
from ..ctrlvocab import sppasCtrlVocab
from ..annotation import sppasAnnotation
from ..annlocation.location import sppasLocation
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval
from ..annlocation.disjoint import sppasDisjoint
from ..annlabel.label import sppasLabel
from ..annlabel.tag import sppasTag

from .basetrs import sppasBaseIO

# ----------------------------------------------------------------------------


class sppasXRA(sppasBaseIO):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS XRA reader and writer.

    xra files are the native file format of the GPL tool SPPAS.

    """
    @staticmethod
    def detect(filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        return root.find('Tier') is not None

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new XRA instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseIO.__init__(self, name)

        self._accept_multi_tiers = True
        self._accept_no_tiers = True
        self._accept_metadata = True
        self._accept_ctrl_vocab = True
        self._accept_media = True
        self._accept_hierarchy = True
        self._accept_point = True
        self._accept_interval = True
        self._accept_disjoint = True
        self._accept_alt_localization = True
        self._accept_alt_tag = True
        self._accept_radius = True
        self._accept_gaps = True
        self._accept_overlaps = True

        self.__format = "1.3"

    # -----------------------------------------------------------------

    def read(self, filename):
        """ Read an XRA file and fill the Transcription.

        :param filename: (str)

        """
        tree = ET.parse(filename)
        root = tree.getroot()
        if "name" in root.attrib:
            self.set_name(root.attrib['name'])

        metadata_root = root.find('Metadata')
        if metadata_root is not None:
            sppasXRA.__read_metadata(self, metadata_root)

        for tier_root in root.findall('Tier'):
            self.__read_tier(tier_root)

        for media_root in root.findall('Media'):
            self.__read_media(media_root)

        hierarchy_root = root.find('Hierarchy')
        if hierarchy_root is not None:
            self.__read_hierarchy(hierarchy_root)

        for vocabulary_root in root.findall('Vocabulary'):
            self.__read_vocabulary(vocabulary_root)

    # -----------------------------------------------------------------

    @staticmethod
    def __read_metadata(meta_object, metadata_root):
        """ Read any kind of metadata. 
        
        :param meta_object: (sppasMetadata)
        :param metadata_root: (ET) XML Element tree root.
        
        """
        if metadata_root is not None:
            for entry_node in metadata_root.findall('Entry'):
                try:
                    key = entry_node.attrib['key'].lower()
                except Exception:
                    # XRA < 1.2
                    key = entry_node.attrib['Key'].lower()
                value = entry_node.text

                meta_object.set_meta(key, value)

    # -----------------------------------------------------------------

    def __read_tier(self, tier_root):
        """ Read a tier.

        :param tier_root: (ET) XML Element tree root.

        """
        name = None
        if "tiername" in tier_root.attrib:
            name = tier_root.attrib['tiername']

        try:
            tid = tier_root.attrib['id']
        except Exception:
            # XRA < 1.2
            tid = tier_root.attrib['ID']
        if name is not None:
            tier = self.create_tier(name)
        else:
            tier = self.create_tier(tid)

        # Set metadata
        sppasXRA.__read_metadata(tier, tier_root.find('Metadata'))
        tier.set_meta("id", tid)

        for annotation_root in tier_root.findall('Annotation'):
            sppasXRA.__read_annotation(tier, annotation_root)

    # -----------------------------------------------------------------

    @staticmethod
    def __read_annotation(tier, annotation_root):
        """ Read an annotation and add it to the tier.

        :param tier: (sppasTier)
        :param annotation_root: (ET) XML Element tree root.

        """
        location_root = annotation_root.find('Location')
        location = sppasXRA.__parse_location(location_root)

        label_root = annotation_root.find('Label')
        label = sppasXRA.__parse_label(label_root)

        annotation = sppasAnnotation(location, label)
        tier.add(annotation)

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_location(location_root):
        """ Read a location and return it.

        :param location_root: (ET) XML Element tree root.
        :returns: (sppasLocation)

        """
        # read list of localizations
        location = sppasLocation()
        for localization_root in list(location_root):
            localization, score = sppasXRA.__parse_localization(localization_root)
            if localization is not None:
                location.append(localization, score)

        if len(location) == 0:
            # XRA < 1.3
            for localization_root in location_root.findall('Localization'):
                for loc_root in list(localization_root):
                    localization, score = sppasXRA.__parse_localization(loc_root)
                    score = localization_root.attrib["score"]
                    location.append(localization, score)

        # read scoremode
        if 'scoremode' in location_root.attrib:
            fun = globals()['__builtins__'][location_root.attrib['scoremode']]
            location.set_function_score(fun)

        return location

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_localization(localization_root):
        """ Read a localization and its score and return it.

        :param localization_root: (ET) XML Element tree root.
        :returns: (sppasLocalization)

        """
        localization = None
        score = None
        loc_str = localization_root.tag.lower()  # to be compatible with all versions

        if 'point' in loc_str:
            localization, score = sppasXRA.__parse_point(localization_root)

        elif 'interval' in loc_str:
            localization, score = sppasXRA.__parse_interval(localization_root)

        elif 'disjoint' in loc_str:
            localization, score = sppasXRA.__parse_disjoint(localization_root)

        return localization, score

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_point(point_node):
        """ Read a localization of type sppasPoint and return it.

        :param point_node: (ET) XML Element node.
        :returns: (sppasPoint)

        """
        # Attribute score
        if 'score' in point_node.attrib:
            score = float(point_node.attrib['score'])
        else:
            score = None

        midpoint_str = point_node.attrib['midpoint']
        try:
            radius_str = point_node.attrib['radius']
        except Exception:
            radius_str = None

        if midpoint_str.isdigit():
            midpoint = int(midpoint_str)
            try:
                radius = int(radius_str)
            except Exception:
                radius = None
        else:
            try:
                midpoint = float(midpoint_str)
                try:
                    radius = float(radius_str)
                except Exception:
                    radius = None
            except Exception:
                midpoint = midpoint_str
                radius = radius_str

        return sppasPoint(midpoint, radius), score

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_interval(interval_root):
        """ Read a localization of type sppasInterval and return it.

        :param interval_root: (ET) XML Element tree root.
        :returns: (sppasInterval)

        """
        # Attribute score
        if 'score' in interval_root.attrib:
            score = float(interval_root.attrib['score'])
        else:
            score = None

        begin_node = interval_root.find('Begin')
        end_node = interval_root.find('End')

        begin, s1 = sppasXRA.__parse_point(begin_node)
        end, s2 = sppasXRA.__parse_point(end_node)

        return sppasInterval(begin, end), score

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_disjoint(disjoint_root):
        """ Read a localization of type sppasDisjoint and return it.

        :param disjoint_root: (ET) XML Element tree root.
        :returns: (sppasDisjoint)

        """
        # Attribute score
        if 'score' in disjoint_root.attrib:
            score = float(disjoint_root.attrib['score'])
        else:
            score = None

        disjoint = sppasDisjoint()
        for interval_root in disjoint_root.findall('Interval'):
            interval = sppasXRA.__parse_interval(interval_root)
            disjoint.append_interval(interval)

        # XRA < 1.3
        if len(disjoint) == 0:
            for interval_root in disjoint_root.findall('TimeInterval'):
                interval = sppasXRA.__parse_interval(interval_root)
                disjoint.append_interval(interval)
            for interval_root in disjoint_root.findall('FrameInterval'):
                interval = sppasXRA.__parse_interval(interval_root)
                disjoint.append_interval(interval)

        return disjoint, score

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_label(label_root):
        """ Read a label and return it.

        :param label_root: (ET) XML Element tree root.
        :returns: (sppasLabel)

        """
        # read list of tags
        label = sppasLabel()
        for tag_root in label_root.findall('Tag'):
            tag, score = sppasXRA.__parse_tag(tag_root)
            label.append(tag, score)

        if len(label) == 0:
            # XRA < 1.3
            for tag_root in label_root.findall('Text'):
                tag, score = sppasXRA.__parse_tag(tag_root)
                label.append(tag, score)

        # read scoremode
        if 'scoremode' in label_root.attrib:
            fun = globals()['__builtins__'][label_root.attrib['scoremode']]
            label.set_function_score(fun)

        return label

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_tag(tag_node):
        """ Read a tag of type sppasTag and return it.

        :param tag_node: (ET) XML Element node.
        :returns: (sppasTag)

        """
        # Attribute score
        if 'score' in tag_node.attrib:
            score = float(tag_node.attrib['score'])
        else:
            score = None

        # Attribute type (str, bool, int, float)
        if 'type' in tag_node.attrib:
            data_type = tag_node.attrib['type']
        else:
            data_type = "str"

        # Tag content
        content = (tag_node.text if tag_node.text is not None else '')
        tag = sppasTag(content, data_type)

        return tag, score

    # -----------------------------------------------------------------

    def __read_media(self, media_root):
        """ Read a media and add it.

        :param media_root: (ET) XML Element tree root.

        """
        # Create a sppasMedia instance
        media_url = media_root.attrib['url']
        media_id = media_root.attrib['id']
        media_mime = None
        if 'mimetype' in media_root.attrib:
            media_mime = media_root.attrib['mimetype']

        media = sppasMedia(media_url, media_id, media_mime)
        self.add_media(media)

        # Add content if any
        content_root = media_root.find('Content')
        if content_root:
            media.set_content(content_root.text)

        # Link to tiers
        for tier_node in media_root.findall('Tier'):
            tier_id = tier_node.attrib['id']
            for tier in self:
                if tier.get_meta("id") == tier_id:
                    tier.set_media(media)

    # -----------------------------------------------------------------

    def __read_hierarchy(self, hierarchy_root):
        """ Read a hierarchy and set it.

        :param hierarchy_root: (ET) XML Element tree root.

        """
        for link_node in hierarchy_root.findall('Link'):
            try:
                hierarchy_type = link_node.attrib['type']
                parent_tier_id = link_node.attrib['from']
                child_tier_id = link_node.attrib['to']
            except Exception:
                # XRA < 1.2
                hierarchy_type = link_node.attrib['Type']
                parent_tier_id = link_node.attrib['From']
                child_tier_id = link_node.attrib['To']

            parent_tier = None
            child_tier = None
            for tier in self:
                if tier.get_meta("id") == parent_tier_id:
                    parent_tier = tier
                if tier.get_meta("id") == child_tier_id:
                    child_tier = tier

            try:
                self.add_hierarchy_link(hierarchy_type, parent_tier, child_tier)
            except Exception as e:
                # print(e)
                logging.info("Corrupted hierarchy link: %s" % str(e))
                pass

    # -----------------------------------------------------------------

    def __read_vocabulary(self, vocabulary_root):
        # Create a CtrlVocab instance
        if 'id' in vocabulary_root.attrib:
            id_vocab = vocabulary_root.attrib['id']
        else:
            # XRA < 1.2
            id_vocab = vocabulary_root.attrib['ID']
        ctrl_vocab = sppasCtrlVocab(id_vocab)
        self.add_ctrl_vocab(ctrl_vocab)

        # Description
        if "description" in vocabulary_root.attrib:
            ctrl_vocab.set_description(vocabulary_root.attrib['description'])

        # Add the list of entries
        for entry_node in vocabulary_root.findall('Entry'):
            # Type of the entry
            if "type" in entry_node.attrib:
                tag_type = entry_node.attrib['type']
            else:
                tag_type = "str"
            entry_text = sppasTag(entry_node.text, tag_type)
            entry_desc = ""
            if "description" in entry_node.attrib:
                entry_desc = entry_node.attrib['description']
            ctrl_vocab.add(entry_text, entry_desc)

        # Link to tiers
        for tier_node in vocabulary_root.findall('Tier'):
            if 'id' in tier_node.attrib:
                tier_id = tier_node.attrib['id']
            else:
                # XRA < 1.2
                tier_id = tier_node.attrib['ID']
            for tier in self:
                if tier.get_meta('id') == tier_id:
                    tier.set_ctrl_vocab(ctrl_vocab)

    # -----------------------------------------------------------------
    # Write XRA 1.3
    # -----------------------------------------------------------------

    def write(self, filename):
        """ Write an XRA file.

        :param filename: (str)

        """
        root = ET.Element('Document')
        root.set('author', 'SPPAS')
        root.set('date', datetime.now().strftime("%Y-%m-%d"))
        root.set('format', self.__format)
        root.set('name', self.get_name())

        metadata_root = ET.SubElement(root, 'Metadata')
        sppasXRA.__format_metadata(metadata_root, self)
        if len(metadata_root.findall('Entry')) == 0:
            root.remove(metadata_root)

        for tier in self:
            tier_root = ET.SubElement(root, 'Tier')
            sppasXRA.__format_tier(tier_root, tier)

        for media in self.get_media_list():
            media_root = ET.SubElement(root, 'Media')
            self.__format_media(media_root, media)

        hierarchy_root = ET.SubElement(root, 'Hierarchy')
        self.__format_hierarchy(hierarchy_root, self._hierarchy)

        for vocabulary in self.get_ctrl_vocab_list():
            vocabulary_root = ET.SubElement(root, 'Vocabulary')
            self.__format_vocabulary(vocabulary_root, vocabulary)

        sppasXRA.indent(root)
        tree = ET.ElementTree(root)
        tree.write(filename, encoding, method="xml")

    # -----------------------------------------------------------------

    @staticmethod
    def __format_metadata(metadata_root, meta_object):
        """ Add metadata of a sppasMetaData object in the tree.

        :param metadata_root: (ET) XML Element tree root.
        :param meta_object: (sppasMetadata)

        """
        for key in meta_object.get_meta_keys():
            value = meta_object.get_meta(key)

            entry = ET.SubElement(metadata_root, 'Entry')
            entry.set('key', key)
            entry.text = value

    # -----------------------------------------------------------------

    @staticmethod
    def __format_tier(tier_root, tier):
        """ Add a tier object in the tree.

        :param tier_root: (ET) XML Element tree root.
        :param tier: (sppasTier)

        """
        # Tier identifier
        tier_id = tier.get_meta('id')
        tier_root.set("id", tier_id)

        # Tier name
        tier_root.set("tiername", tier.get_name())

        # Tier Metadata
        tier.pop_meta('id')
        metadata_root = ET.SubElement(tier_root, 'Metadata')
        sppasXRA.__format_metadata(metadata_root, tier)
        if len(metadata_root.findall('Entry')) == 0:
            tier_root.remove(metadata_root)
        tier.set_meta('id', tier_id)

        # Tier annotations list
        for annotation in tier:
            annotation_root = ET.SubElement(tier_root, 'Annotation')
            sppasXRA.__format_annotation(annotation_root, annotation)

    # -----------------------------------------------------------------

    @staticmethod
    def __format_annotation(annotation_root, annotation):
        """ Add an annotation object in the tree.

        :param annotation_root: (ET) XML Element tree root.
        :param annotation: (sppasAnnotation)

        """
        location_root = ET.SubElement(annotation_root, 'Location')
        sppasXRA.__format_location(location_root, annotation.get_location())

        label_root = ET.SubElement(annotation_root, 'Label')
        sppasXRA.__format_label(label_root, annotation.get_label())

    # -----------------------------------------------------------------

    @staticmethod
    def __format_location(location_root, location):
        """ Add a location object in the tree.

        :param location_root: (ET) XML Element tree root.
        :param location: (sppasLocation)

        """
        if location.get_function_score() != max:
            location_root.set('scoremode', location.get_function_score().__name__)

        for localization, score in location:
            if localization.is_point():
                point_node = ET.SubElement(location_root, 'Point')
                sppasXRA.__format_point(point_node, localization)
                if score is not None:
                    point_node.set('score', u(str(score)))

            elif localization.is_interval():
                interval_root = ET.SubElement(location_root, 'Interval')
                sppasXRA.__format_interval(interval_root, localization)
                if score is not None:
                    interval_root.set('score', u(str(score)))

            elif localization.IsTimeDisjoint():
                disjoint_root = ET.SubElement(location_root, 'Disjoint')
                sppasXRA.__format_disjoint(disjoint_root, localization)
                if score is not None:
                    disjoint_root.set('score', u(str(score)))

    # -----------------------------------------------------------------

    @staticmethod
    def __format_point(point_node, point):
        """ Add a point object in the tree.

        :param point_node: (ET) XML Element node.
        :param point: (sppasPoint)

        """
        point_node.set('midpoint', u(str(point.get_midpoint())))
        if point.get_radius() is not None:
            point_node.set('radius', u(str(point.get_radius())))

    # -----------------------------------------------------------------

    @staticmethod
    def __format_interval(interval_root, interval):
        """ Add an interval object in the tree.

        :param interval_root: (ET) XML Element node.
        :param interval: (sppasInterval)

        """
        begin = ET.SubElement(interval_root, 'Begin')
        sppasXRA.__format_point(begin, interval.get_begin())

        end = ET.SubElement(interval_root, 'End')
        sppasXRA.__format_point(end, interval.get_end())

    # -----------------------------------------------------------------

    @staticmethod
    def __format_disjoint(disjoint_root, disjoint):
        """ Add a disjoint object in the tree.

        :param disjoint_root: (ET) XML Element node.
        :param disjoint: (sppasDisjoint)

        """
        for interval in disjoint:
            interval_root = ET.SubElement(disjoint_root, 'Interval')
            sppasXRA.__format_interval(interval_root, interval)

    # -----------------------------------------------------------------

    @staticmethod
    def __format_label(label_root, label):
        """ Add a label object in the tree.

        :param label_root: (ET) XML Element tree root.
        :param label: (sppasLabel)

        """
        if label.get_function_score() != max:
            label_root.set('scoremode', label.get_function_score().__name__)

        for tag, score in label:
            tag_node = ET.SubElement(label_root, 'Tag')
            if score is not None:
                tag_node.set("score", str(score))
            sppasXRA.__format_tag(tag_node, tag)

    # -----------------------------------------------------------------

    @staticmethod
    def __format_tag(tag_node, tag):
        """ Add a tag object in the tree.

        :param tag_node: (ET) XML Element node.
        :param tag: (sppasTag)

        """
        tag_node.set('type', tag.get_type())
        tag_node.text = tag.get_content()

    # -----------------------------------------------------------------

    def __format_media(self, media_root, media):
        """ Add a media object in the tree.

        :param media_root: (ET) XML Element tree root.
        :param media: (sppasMedia)

        """
        # Set attribute
        media_root.set('id', media.get_name())
        media_root.set('url', media.get_filename())
        media_root.set('mimetype', media.get_mime_type())

        # Element Tier
        for tier in self:
            if tier.get_media() == media:
                tier_node = ET.SubElement(media_root, 'Tier')
                tier_node.set('id', tier.get_meta('id'))

        # Element Metadata
        if len(media.get_meta_keys()) > 0:
            metadata_root = ET.SubElement(media_root, 'Metadata')
            self.__format_metadata(metadata_root, media)

        # Element Content
        if len(media.get_content()) > 0:
            content_node = ET.SubElement(media_root, 'Content')
            content_node.text = media.get_content()

    # -----------------------------------------------------------------

    def __format_hierarchy(self, hierarchy_root, hierarchy):
        """ Add a hierarchy object in the tree.

        :param hierarchy_root: (ET) XML Element tree root.
        :param hierarchy: (sppasHierarchy)

        """
        for child_tier in self:
            parent_tier = hierarchy.get_parent(child_tier)
            if parent_tier is not None:
                link_type = hierarchy.get_hierarchy_type(child_tier)
                link = ET.SubElement(hierarchy_root, 'Link')
                link.set('type', link_type)
                link.set('from', parent_tier.get_meta('id'))
                link.set('to', child_tier.get_meta('id'))

    # -----------------------------------------------------------------

    def __format_vocabulary(self, vocabulary_root, vocabulary):
        """ Add a controlled vocabulary object in the tree.

         :param vocabulary_root: (ET) XML Element tree root.
         :param vocabulary: (sppasCtrlVocab)

        """
        # Set attribute
        vocabulary_root.set('id', vocabulary.get_name())
        if len(vocabulary.get_description()) > 0:
            vocabulary_root.set('description', vocabulary.get_description())

        # Write the list of entries (an entry is a sppasTag instance)
        for entry in vocabulary:
            entry_node = ET.SubElement(vocabulary_root, 'Entry')
            entry_node.text = entry.get_content()
            if entry.get_type() != "str":
                entry_node.set('type', entry.get_type())
            if len(vocabulary.get_tag_description(entry)) > 0:
                entry_node.set('description', vocabulary.get_tag_description(entry))

        # Element Tier
        for tier in self:
            if tier.get_ctrl_vocab() == vocabulary:
                tier_node = ET.SubElement(vocabulary_root, 'Tier')
                tier_node.set('id', tier.get_meta('id'))

    # -----------------------------------------------------------------

    @staticmethod
    def indent(elem, level=0):
        """ Pretty indent.
        http://effbot.org/zone/element-lib.htm#prettyprint

        """
        i = "\n" + level * "\t"
        if len(elem) > 0:
            if not elem.text or not elem.text.strip():
                elem.text = i + "\t"
            if not elem.tail or not elem.tail.strip():
                if level < 2:
                    elem.tail = "\n" + i
                else:
                    elem.tail = i
            for elem in elem:
                sppasXRA.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i