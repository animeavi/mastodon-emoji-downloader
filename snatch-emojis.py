#! /usr/bin/env python3

from os.path import isdir
from requests import get
from typing import List, Dict
import argparse
import os
from tqdm import tqdm

args = argparse.ArgumentParser("snatch-emojis")
args.add_argument('--instance', '-i', nargs=1, required=True,
                  help='instance to download all emojis from')

URL_GET_EMOJIS = r'https://{instance}/api/v1/custom_emojis'


class Emoji(object):
    shortcode: str
    url: str
    static_url: str
    visible_in_picker: bool
    category: str

    def __init__(self, emoji_object: Dict) -> None:
        for field in set(["shortcode",
                          "url",
                          "static_url",
                          "visible_in_picker",
                          "category"]):
            setattr(self, field, emoji_object[field])

    def __str__(self) -> str:
        return f"<Emoji shortcode: {self.shortcode}, cat: {self.category}>"

    def __repr__(self) -> str:
        return self.__str__()

def get_emojis(instance: str) -> List:
    r = get(URL_GET_EMOJIS.format(instance=instance))
    r.raise_for_status()
    return r.json()


def download_emoji(instance: str, emoji: Emoji):
    p = os.path
    if not p.lexists(instance) or not p.isdir(instance):
        os.mkdir(instance)

    outname = emoji.shortcode.replace(':', '')
    _, filext = p.splitext(emoji.url)
    category = emoji.category

    outdir = p.join(instance, category)
    outfile = p.join(outdir, outname) + f"{filext}"

    if p.isfile(outfile):
        # no need to download again
        return

    if not p.lexists(outdir) or not p.isdir(outdir):
        os.mkdir(outdir)

    r = get(emoji.url)
    r.raise_for_status()

    with open(outfile, 'wb') as f:
        f.write(r.content)


def main(p):
    instance = p.instance[0]
    e = get_emojis(instance)
    emojis = [Emoji(i) for i in e]

    with tqdm(unit='emojis', total=len(emojis)) as pb:
        for emoji in emojis:
            pb.update()
            pb.write(str(emoji))
            download_emoji(instance, emoji)


if __name__ == '__main__':
    p = args.parse_args()
    main(p)
