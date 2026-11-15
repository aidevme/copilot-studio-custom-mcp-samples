// Fetch all aidevme.com tags, posts and categories from the WordPress REST API and download them as one
// JSON file, aidevme_taxonomy.json. Run in the DevTools console of a browser tab open on https://aidevme.com
// (same origin, so no CORS or firewall issues). Public GET requests only; no login needed.
(async () => {
  const base = `${location.origin}/wp-json/wp/v2`;
  const collections = {
    tags: "tags?per_page=100&_fields=id,name,slug,count,description,link",
    posts: "posts?per_page=100&_fields=id,title,slug,link,date,modified,categories,tags",
    categories: "categories?per_page=100&_fields=id,name,slug,count,description,parent,link",
  };

  async function fetchAll(path) {
    const items = [];
    let page = 1;
    let totalPages = 1;
    do {
      const response = await fetch(`${base}/${path}&page=${page}`, { headers: { Accept: "application/json" } });
      if (!response.ok) {
        throw new Error(`${path} page ${page}: HTTP ${response.status}` +
          ([401, 403, 404].includes(response.status) ? " (a security plugin may be blocking the REST API)" : ""));
      }
      totalPages = Number(response.headers.get("X-WP-TotalPages") || 1);
      items.push(...(await response.json()));
      page += 1;
    } while (page <= totalPages);
    return items;
  }

  const result = { site: location.origin, retrieved: new Date().toISOString(), source: "browser fetch()" };
  for (const [name, path] of Object.entries(collections)) {
    result[name] = await fetchAll(path);
  }
  result.totals = Object.fromEntries(Object.keys(collections).map((name) => [name, result[name].length]));

  const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
  const link = Object.assign(document.createElement("a"), {
    href: URL.createObjectURL(blob),
    download: "aidevme_taxonomy.json",
  });
  link.click();
  console.log("aidevme_taxonomy.json downloaded", result.totals);
  return result;
})();
