# rmxbot

The project that runs proximity-bot; it uses scrasync (https://github.com/dbrtk/scrasync) and nlp (https://github.com/dbrtk/nlp); these should be deployed on their own servers. The server that runs rmxbot requires Pyhton 3, Mongodb and Redis; all other dependencies will be installed automatically.


Package requirements are:
* rmxbot-tpl (https://github.com/dbrtk/rmxbot-tpl);
* rmx (https://github.com/dbrtk/rmx).

## Configuration of rmxbot
These variables should be updated:
* DEFAULT_CRAWL_DEPTH - the depth set on the crawler;
* NLP_ENDPOINT - the url of the server that hosts nlp;
* SCRASYNC_ENDPOINT - the url of the server that hosts scrasync;
* DATA_ROOT - the path to the directory that will contain the data files (corpora, matrices);
* CORPUS_MAX_SIZE - the maximal number of documents a corpus can ocntain.

