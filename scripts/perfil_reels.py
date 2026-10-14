"""Lista os reels de um perfil público do Instagram (sem login) e imprime os links dos mais vistos.
Também salva o perfil (bio, legendas, números) em <pasta>/perfil.json para a análise."""
import json, sys, urllib.request

user, quantos, pasta = sys.argv[1].lstrip("@"), int(sys.argv[2]), sys.argv[3]
H = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Instagram 300.0",
     "X-IG-App-ID": "936619743392459", "Accept": "*/*"}
dados = None
for url in (f"https://i.instagram.com/api/v1/users/web_profile_info/?username={user}",
            f"https://www.instagram.com/api/v1/users/web_profile_info/?username={user}"):
    try:
        dados = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30).read())
        break
    except Exception as e:
        print(f"[perfil] {url}: {e}", file=sys.stderr)
if not dados:
    sys.exit(0)
u = dados["data"]["user"]
posts = []
for ed in u["edge_owner_to_timeline_media"]["edges"]:
    n = ed["node"]
    cap = (n.get("edge_media_to_caption", {}).get("edges") or [{}])[0].get("node", {}).get("text", "")
    posts.append({"code": n["shortcode"], "video": n.get("is_video"), "views": n.get("video_view_count") or 0,
                  "likes": n.get("edge_liked_by", {}).get("count") or n.get("edge_media_preview_like", {}).get("count"),
                  "comentarios": n.get("edge_media_to_comment", {}).get("count"), "tipo": n.get("__typename"),
                  "legenda": cap[:600], "capa": n.get("display_url")})
json.dump({"usuario": user, "bio": u.get("biography"), "seguidores": u.get("edge_followed_by", {}).get("count"),
           "posts_total": u.get("edge_owner_to_timeline_media", {}).get("count"), "posts": posts},
          open(f"{pasta}/perfil.json", "w"), ensure_ascii=False, indent=1)
videos = sorted([p for p in posts if p["video"]], key=lambda p: -p["views"])[:quantos]
print(" ".join(f"https://www.instagram.com/reel/{p['code']}/" for p in videos))
