## Linguarticle 📰🖋

### General info

Linguarticle is an article translation web application.</br>
The idea of an app is to be a place where you can not only save, read, and translate articles, but also save new words to your own dictionary to learn a new language.<br/>
For now articles from BBC and CNN are rendering correctly.<br/>
The translation is from English to Ukrainian.<br/>

To translate an Article input its url to scrape it with <a href="https://scrapy.org/">Scrapy</a>.<br/>
Pick a saved article from your list to visualize its content.<br/>
Select words to receive <a href="https://github.com/prataffel/deep_translator">translation</a> in Ukrainian.<br/>
You can add words to your personal dictionary.</p>

*Front-End files can be found in `apps/static` and `apps/templates`*
### Preview | [YouTube Video](https://youtu.be/BUAlJ0DojiU)

<img src="https://i.imgur.com/QiJLvC8.png" width="800">
<img src="https://i.imgur.com/icHwjxt.png" width="800">
<h4>Commands</h4>
Run: <code>make d-run</code><br/>
Run locally: <code>make d-run-local-dev</code><br/>
Purge: <code>make d-purge</code><br/>

<h4>API Documentation</h4>
URLs: <code>/swagger/</code>, <code>/redoc/</code><br/>
