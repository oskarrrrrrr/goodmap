from os.path import dirname

from flask import Blueprint, make_response, render_template
from markupsafe import Markup

from goodmap.config import Config


def create_blog_blueprint(db, config: Config, babel):
    url_prefix = config.blog_prefix
    blog = Blueprint(
        "blog",
        __name__,
        url_prefix=url_prefix,
        template_folder=f"{dirname(__file__)}/../templates",
    )

    def locale():
        return babel.locale_selector_func()

    @blog.app_template_filter()
    def markdown(text):
        return Markup(text)

    @blog.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html", title="404"), 404

    @blog.route("/", methods=["GET"])
    def index():
        lang = locale()
        return render_template("blog.html", posts=db.get_all_posts(lang))

    @blog.route("/feed", methods=["GET"])
    def get_feed():
        lang = locale()
        response = make_response(render_template("feed.xml", posts=db.get_all_posts(lang)))
        response.headers["Content-Type"] = "application/xml"
        return response

    @blog.route("/<post_slug>", methods=["GET"])
    def get_post(post_slug):
        if post := db.get_post(post_slug):
            return render_template(
                "post.html",
                post=post,
                post_slug=post_slug,
            )
        else:
            return page_not_found("no such page")

    @blog.route("/page/<path:page_slug>", methods=["GET"])
    def get_page(
        page_slug,
    ):  # TODO refactor to share code with get_post since they are very similar
        if page := db.get_page(page_slug):
            if cover_image := page.get("coverImage"):
                cover_image_url = cover_image["url"]
            else:
                cover_image_url = None
            return render_template("page.html", page=page, cover_image=cover_image_url)
        else:
            return page_not_found("no such page")

    @blog.route("/tag/<path:tag>", methods=["GET"])
    def get_posts_from_tag(tag):
        lang = locale()
        posts = db.get_posts_by_tag(tag, lang)
        return render_template("blog.html", posts=posts, subtitle=f" - tag: {tag}")

    return blog
