# huggingface-spaces-cdn

an image/content cdn hosted on hf spaces.

## installation

1. create a new [hf space](https://huggingface.co/new-space), set sdk to gradio
2. upload `app.py` and `requirements.py` to the space
3. wait for it to build
4. profit & enjoy - give this repo a star if you find it useful!

nb: you may need to create a script to auto-restart the space - free hf spaces sleep after ~48 hours.

## usage

GET/POST: `<base_url>?url=<url>` - returns the binary of the content and all the headers
DELETE: `<base_url>?url=<url>` - clears the cache of a file

## legal notice

educational purposes only. check hf's [tos](https://huggingface.co/terms-of-service) before hosting it. you are responsible for your usage of this.

## license

this software may be used for personal/non-commercial use only. this software is not open sourced. redistribution of this code is allowed, but modification is not.

the software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. in no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.
