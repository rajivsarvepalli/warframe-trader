"""The different views for the flask application."""
from flask import render_template, request, send_from_directory, make_response, abort
from flask.wrappers import Response
from flask_cachecontrol import (
    cache_for,
    cache,
    dont_cache,
    ResponseIsSuccessful,
    Always,
)

from src import app
from src import cache
from src import storage
from src import w_secret
import json
import os
from typing import List, Union, Dict, Any
import hashlib
import hmac
import git
import math


@cache.memoize(timeout=600)
def get_items(only_name: bool = True) -> Union[List[str], Dict[str, str]]:
    """Get the items from firebase cloud storage.

    Gets warframe market items from the firebase cloud storage.

    Args:
        only_name: Whether to include only the item names. If this is
            true, then only the names of the items are returned in a list,
            otherwise a dictionary of items names to item urls is returned.

    Returns:
        A list of warframe item names, or a dictionary of item names to url names.
    """
    blob = storage.bucket.get_blob("items/items.json")
    json_str = blob.download_as_string()
    items = json.loads(json_str)
    items = items["items"]
    if only_name:
        items_info = []
        for item in items:
            items_info.append(item["item_name"])
    else:
        market_url = "https://warframe.market/items/%s"
        items_info = {}
        for item in items:
            url_link = market_url % (item["url_name"])
            items_info[item["item_name"]] = url_link
    return items_info


@cache.memoize(timeout=600)
def get_primes() -> Dict:
    """Get the primes rankings from firebase."""
    blob = storage.bucket.blob("prime/prime_ranking.json")
    json_str = blob.download_as_string()
    prime_ranks = json.loads(json_str)
    return prime_ranks


@cache.memoize(timeout=60)
def get_stats(item_name: str) -> Dict:
    """Get the statistics from firebase storage."""
    item_name = item_name.lower()
    blob = storage.bucket.blob("stats/" + str(item_name) + "_stats.json")
    json_str = blob.download_as_string()
    stats = json.loads(json_str)
    return stats


def is_valid_signature(x_hub_signature, data, private_key):
    """Check for valid signature to make sure we do not update unnecessarily."""
    hash_algorithm, github_signature = x_hub_signature.split("=", 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, "latin-1")
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)


@app.errorhandler(404)
def not_found(e) -> Response:
    """Page not found."""
    item_names = get_items()
    return make_response(render_template("404.html", items=item_names), 404)


@app.errorhandler(400)
def bad_request(e) -> Response:
    """Bad request."""
    item_names = get_items()
    return make_response(render_template("400.html", items=item_names), 400)


@app.errorhandler(500)
def server_error(e) -> Response:
    """Internal server error."""
    item_names = get_items()
    return make_response(render_template("500.html", items=item_names), 500)


@app.after_request
def add_header(response) -> Response:
    """Adding headers."""
    response.headers["X-UA-Compatible"] = "IE=Edge,chrome=1"
    return response


@app.route("/favicon.ico")
def favicon() -> Response:
    """Route for the favicon."""
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/")
@app.route("/home", methods=["GET"])
@cache_for(only_if=ResponseIsSuccessful, hours=3)
def home() -> str:
    """ Renders the home page """
    if request.method == "GET":
        # collect items from warframe item database

        item_names = get_items()
        return render_template(
            "index.html",
            items=item_names,
        )


@app.route("/predict", methods=["POST", "GET"])
@dont_cache(only_if=Always)
def predict() -> str:
    """View for the statistics page."""
    item_to_find = request.form["search_items"]
    # compute url for warframe data based on name
    # do some checking to make sure name is valid
    # save all the data required in firebase
    warframe_data_url = "https://demo-live-data.highcharts.com/aapl-ohlcv.json"
    item_names = get_items()
    if item_to_find not in item_names:
        return render_template("404.html")
    stats = get_stats(item_to_find)
    warframe_data = []
    
    ranked_item = False
    if len(stats["mod_ranks"]) > 0:
        ranked_item = True
        for d, o, h, l, c, v, ap, mr in zip(
            stats["dates"],
            stats["open_prices"],
            stats["max_prices"],
            stats["min_prices"],
            stats["closed_prices"],
            stats["volumes"],
            stats["avg_prices"],
            stats["mod_ranks"],
        ):
            warframe_data.append([d, o, h, l, c, v, ap, mr])
    else:
        for d, o, h, l, c, v, ap in zip(
            stats["dates"],
            stats["open_prices"],
            stats["max_prices"],
            stats["min_prices"],
            stats["closed_prices"],
            stats["volumes"],
            stats["avg_prices"],
        ):
            warframe_data.append([d, o, h, l, c, v, ap])
    return render_template(
        "charts.html",
        warframe_data_url=warframe_data_url,
        warframe_data=warframe_data,
        item_name=item_to_find.title(),
        items=item_names,
        ranked_item=ranked_item,
    )


@app.route("/primes_sell", methods=["GET"])
@cache_for(only_if=ResponseIsSuccessful, hours=3)
def primes_sell() -> str:
    """View for the prime ranking selling page."""
    items_to_urls = get_items(only_name=False)
    prime_ranks = get_primes()
    # display prime ranks in some pretty tabular format
    prime_ranks = prime_ranks["sell"]
    table_data = []
    for index in prime_ranks["Item Name"]:
        name = prime_ranks["Item Name"][index]
        type_item = prime_ranks["Item Type"][index]
        score = prime_ranks["Metric"][index]
        if math.isnan(score):
            score = 0
        url_market = items_to_urls[name]
        table_data.append([name, type_item, score, url_market])
    table_data.sort(key=lambda x: x[2], reverse=True)
    for i, t in enumerate(table_data):
        t.insert(0, i + 1)
    return render_template(
        "table.html",
        table_data=table_data,
        items=list(items_to_urls.keys()),
        buy_sell="sell",
    )


@app.route("/primes_buy", methods=["GET"])
@cache_for(only_if=ResponseIsSuccessful, hours=3)
def primes_buy() -> str:
    """View for the prime ranking buying page."""
    items_to_urls = get_items(only_name=False)
    prime_ranks = get_primes()
    # display prime ranks in some pretty tabular format
    prime_ranks = prime_ranks["buy"]
    table_data = []
    for index in prime_ranks["Item Name"]:
        name = prime_ranks["Item Name"][index]
        type_item = prime_ranks["Item Type"][index]
        score = 1 - prime_ranks["Metric"][index]
        if math.isnan(score):
            score = 0
        url_market = items_to_urls[name]
        table_data.append([name, type_item, score, url_market])
    table_data.sort(key=lambda x: x[2], reverse=True)
    for i, t in enumerate(table_data):
        t.insert(0, i + 1)
    return render_template(
        "table.html",
        table_data=table_data,
        items=list(items_to_urls.keys()),
        buy_sell="buy",
    )


@app.route("/about", methods=["GET"])
@cache_for(only_if=ResponseIsSuccessful, hours=3)
def about() -> str:
    """View for the about page."""
    item_names = get_items()
    return render_template(
        "about.html",
        items=item_names,
    )


@app.route("/update_server", methods=["POST"])
def webhook() -> None:
    """"Updates the flask application on a push to main branch on GitHub."""
    if request.method != "POST":
        return "OK"
    else:
        abort_code = 418
        # Do initial validations on required headers
        if "X-Github-Event" not in request.headers:
            abort(abort_code)
        if "X-Github-Delivery" not in request.headers:
            abort(abort_code)
        if "X-Hub-Signature" not in request.headers:
            abort(abort_code)
        if not request.is_json:
            abort(abort_code)
        if "User-Agent" not in request.headers:
            abort(abort_code)
        ua = request.headers.get("User-Agent")
        if not ua.startswith("GitHub-Hookshot/"):
            abort(abort_code)

        event = request.headers.get("X-GitHub-Event")
        if event == "ping":
            return json.dumps({"msg": "Hi!"})
        if event != "push":
            return json.dumps({"msg": "Wrong event type"})

        x_hub_signature = request.headers.get("X-Hub-Signature")
        # webhook content type should be application/json for request.data to have the payload
        # request.data is empty in case of x-www-form-urlencoded
        if not is_valid_signature(x_hub_signature, request.data, w_secret):
            print("Deploy signature failed: {sig}".format(sig=x_hub_signature))
            abort(abort_code)

        payload = request.get_json()
        if payload is None:
            print("Deploy payload is empty: {payload}".format(payload=payload))
            abort(abort_code)

        if payload["ref"] != "refs/heads/main":
            return json.dumps({"msg": "Not main; ignoring"})

        repo = git.Repo("/home/rajivsarvepalli/warframe-trader")
        origin = repo.remotes.origin

        pull_info = origin.pull()

        if len(pull_info) == 0:
            return json.dumps({"msg": "Didn't pull any information from remote!"})
        if pull_info[0].flags > 128:
            return json.dumps({"msg": "Didn't pull any information from remote!"})

        commit_hash = pull_info[0].commit.hexsha
        build_commit = f'build_commit = "{commit_hash}"'
        print(f"{build_commit}")
        return "Updated PythonAnywhere server to commit {commit}".format(
            commit=commit_hash
        )
