"""
    Books look like:
    <BOOK><TITLE>Alice's Adventures in Wonderland</TITLE>
            <AUTHOR>Lewis Carroll</AUTHOR>

        <CHAPTER><TITLE>Down the Rabbit-Hole</TITLE>
            <p>
            Alice was beginning to get very tired of sitting by her sister on the
            bank, and of having nothing to do: once or twice she had peeped into the
            book her sister was reading, but it had no pictures or conversations in
            it, 'and what is the use of a book,' thought Alice 'without pictures or
            conversation?'
            </p>

            <pre>
            * * * *            * * *
            </pre>
        </CHAPTER>
    </BOOK>

    and generally have more than one chapter


    return something like
    book = { 'title': "Alice's Adventures in Wonderland",
                'author': "Lewis Carroll",
                'chapters': [
                    {'title': "Down the Rabbit-Hole",
                     'pages': [
                            "Alice was beginning to get very tired...",
                            "<pre>\n* * * * ...",
                            ]
                    },
                }
"""

def parsetags(tags, text):
    """expects a tuple of non-nested tags, and text"""
    tags = ['<%s>'%t for t in tags]

    def next( txt):
        winner = True
        while winner:
            winner = False
            for tag in tags:
                if tag in txt: 
                    if not winner or txt.find(tag) < winner[1]: 
                        winner = (tag, txt.find(tag)) 

            if winner: 
                tag = winner[0]
                endtag = '</%s>'% tag.strip('<>')
                start = txt.find( tag)
                end = txt.find( endtag)+len(endtag)

                yield txt[start:end].strip('\r\n ')
                txt = txt[ end:]

    return [s for s in next( text)]

def striptags(tag, text):
    return text.replace('<%s>'%tag,'').replace('</%s>'%tag,'')



from os.path import join
def parsebook( text = 'alice.xml'):
    text = open( join('lib/' + text)).read()

    book = { 'author': striptags( 'AUTHOR', parsetags(('AUTHOR',), text)[0]),
                'title': striptags( 'TITLE', parsetags(('TITLE',), text)[0]),
                'chapters': [],
            }

    chapters = parsetags( ('CHAPTER',), text)
    for chapter in chapters:
        book['chapters'].append( { 'title': striptags( 'TITLE', parsetags(('TITLE',), chapter)[0]),
                                            'pages': parsetags( ('p','pre'), chapter)
                                            })
    return book


class Book:
    def __init__(self, text='alice.xml'):
        self.book = parsebook( text)
        self.boards = []

        self.mkBoards()

    def mkBoards(self):
        from board import Board, calcdimension
        for chapter in self.book['chapters']:
            length = len(chapter['pages'])
            B = Board( calcdimension(length), length)
            B.Book = self

            if chapter is not self.book['chapters'][-1]:
                B.maze[ B.solution[-1]].nextboard = True
            if chapter is not self.book['chapters'][0]:
                B.maze[ B.solution[0]].prevboard = True

            for i in range( length):
                B.maze[ B.solution[i]].desc = chapter['pages'][i]

            self.boards.append( B)


