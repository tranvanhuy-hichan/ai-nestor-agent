"""Danh muc dich vu MCP tu xa da kiem chung.

Moi muc da duoc thu bang chinh luong cua Nestor (SDK MCP) tren dia chi that: `oauth` = lay duoc dia chi dang nhap (kham pha + dang ky client dong
thanh cong), `open` = ket noi khong can dang nhap va liet ke duoc cong cu, `token` = can token ca nhan (nha cung cap khong cho tu dang ky).
Cac dich vu thu nhung khong dung duoc (Slack, HubSpot, Box, Calendly, Gamma, Figma...) khong dua vao day.
"""

GROUPS = [
    {"id": "dev", "label": {"vi": "Lập trình và triển khai", "en": "Code and deployment"}},
    {"id": "data", "label": {"vi": "Dữ liệu và hạ tầng", "en": "Data and infrastructure"}},
    {"id": "search", "label": {"vi": "Tìm kiếm và tài liệu", "en": "Search and docs"}},
    {"id": "work", "label": {"vi": "Công việc và cộng tác", "en": "Work and collaboration"}},
    {"id": "design", "label": {"vi": "Thiết kế và website", "en": "Design and websites"}},
    {"id": "biz", "label": {"vi": "Kinh doanh và thanh toán", "en": "Business and payments"}},
    {"id": "ai", "label": {"vi": "Trí tuệ nhân tạo và mô hình", "en": "AI and models"}},
    {"id": "sec", "label": {"vi": "Bảo mật và an toàn", "en": "Security and safety"}},
    {"id": "media", "label": {"vi": "Truyền thông và mạng xã hội", "en": "Media and social"}},
]


def _s(id, name, url, group, auth, vi, en, color="6B7280", transport="http", **extra):
    return {"id": id, "name": name, "url": url, "group": group, "auth": auth, "transport": transport, "color": color, "desc": {"vi": vi, "en": en}, **extra}


GITHUB_TOKEN = {"header": "Authorization", "prefix": "Bearer ", "help_url": "https://github.com/settings/personal-access-tokens/new",
                "hint": {"vi": "Tạo một Personal Access Token trên GitHub (chỉ cấp quyền cần thiết) rồi dán vào đây.", "en": "Create a Personal Access Token on GitHub (grant only the permissions you need) and paste it here."}}

BRAVE_TOKEN = {"header": "X-Subscription-Token", "prefix": "", "help_url": "https://brave.com/search/api/",
               "hint": {"vi": "Dán API Key Brave Search vào đây để tìm kiếm web.", "en": "Paste your Brave Search API key here."}}

PERPLEXITY_TOKEN = {"header": "Authorization", "prefix": "Bearer ", "help_url": "https://www.perplexity.ai/settings/api",
                    "hint": {"vi": "Dán Perplexity API key vào đây.", "en": "Paste your Perplexity API key here."}}

SLACK_TOKEN = {"header": "Authorization", "prefix": "Bearer ", "help_url": "https://api.slack.com/apps",
               "hint": {"vi": "Dán Bot User OAuth Token của Slack (xoxb-...) vào đây.", "en": "Paste your Slack Bot User OAuth Token (xoxb-...) here."}}

DISCORD_TOKEN = {"header": "Authorization", "prefix": "Bot ", "help_url": "https://discord.com/developers/applications",
                 "hint": {"vi": "Dán Discord Bot Token vào đây.", "en": "Paste your Discord Bot Token here."}}

SHODAN_TOKEN = {"header": "X-API-Key", "prefix": "", "help_url": "https://account.shodan.io/",
                "hint": {"vi": "Dán Shodan API Key vào đây để quét mạng và bảo mật.", "en": "Paste your Shodan API key here."}}

SERVICES = [
    # --- Lap trinh va trien khai
    _s("github", "GitHub", "https://api.githubcopilot.com/mcp/", "dev", "token", "Đọc repo, issue, pull request và Actions bằng token cá nhân.", "Read repos, issues, pull requests and Actions with a personal token.", "181717", token=GITHUB_TOKEN),
    _s("gitlab", "GitLab", "https://gitlab.com/api/v4/mcp", "dev", "oauth", "Xem project, issue và merge request trên GitLab.", "View projects, issues and merge requests on GitLab.", "FC6D26"),
    _s("vercel", "Vercel", "https://mcp.vercel.com", "dev", "oauth", "Xem project, deployment và log trên Vercel.", "Inspect projects, deployments and logs on Vercel.", "000000"),
    _s("netlify", "Netlify", "https://netlify-mcp.netlify.app/mcp", "dev", "oauth", "Quản lý site và deploy trên Netlify.", "Manage sites and deploys on Netlify.", "00C7B7"),
    _s("cloudflare-bindings", "Cloudflare Workers", "https://bindings.mcp.cloudflare.com/mcp", "dev", "oauth", "Quản lý Workers, KV, D1, R2 trên Cloudflare.", "Manage Workers, KV, D1 and R2 on Cloudflare.", "F38020"),
    _s("cloudflare-observability", "Cloudflare Observability", "https://observability.mcp.cloudflare.com/mcp", "dev", "oauth", "Xem log và số liệu của Workers trên Cloudflare.", "Read Workers logs and analytics on Cloudflare.", "F38020"),
    _s("cloudflare-docs", "Cloudflare Docs", "https://docs.mcp.cloudflare.com/mcp", "dev", "open", "Tra cứu tài liệu Cloudflare, không cần đăng nhập.", "Search the Cloudflare docs. No sign-in needed.", "F38020"),
    _s("sentry", "Sentry", "https://mcp.sentry.dev/mcp", "dev", "oauth", "Xem lỗi, issue và hiệu năng ứng dụng trong Sentry.", "Look at errors, issues and performance in Sentry.", "362D59"),
    _s("datadog", "Datadog", "https://mcp.datadoghq.com/api/unstable/mcp-server/mcp", "dev", "oauth", "Truy vấn log, metric và monitor trong Datadog.", "Query logs, metrics and monitors in Datadog.", "632CA6"),
    _s("jam", "Jam", "https://mcp.jam.dev/mcp", "dev", "oauth", "Đọc báo cáo lỗi kèm bản ghi màn hình từ Jam.", "Read bug reports with screen recordings from Jam.", "F2A93B"),
    _s("context7", "Context7", "https://mcp.context7.com/mcp", "dev", "open", "Tài liệu thư viện lập trình luôn mới nhất, không cần đăng nhập.", "Up-to-date library documentation. No sign-in needed.", "059669"),
    _s("deepwiki", "DeepWiki", "https://mcp.deepwiki.com/mcp", "dev", "open", "Hỏi đáp về mã nguồn các repo GitHub công khai.", "Ask questions about public GitHub repositories.", "2563EB"),
    _s("microsoft-learn", "Microsoft Learn", "https://learn.microsoft.com/api/mcp", "dev", "open", "Tra cứu tài liệu Microsoft và Azure, không cần đăng nhập.", "Search Microsoft and Azure docs. No sign-in needed.", "0078D4"),
    # --- Du lieu va ha tang
    _s("neon", "Neon", "https://mcp.neon.tech/mcp", "data", "oauth", "Quản lý project và chạy SQL trên Neon Postgres.", "Manage projects and run SQL on Neon Postgres.", "00E599"),
    _s("supabase", "Supabase", "https://mcp.supabase.com/mcp", "data", "oauth", "Quản lý project, bảng và truy vấn trên Supabase.", "Manage projects, tables and queries on Supabase.", "3FCF8E"),
    _s("posthog", "PostHog", "https://mcp.posthog.com/mcp", "data", "oauth", "Xem phân tích sản phẩm, feature flag và thí nghiệm.", "Browse product analytics, feature flags and experiments.", "F9BD2B"),
    _s("apify", "Apify", "https://mcp.apify.com", "data", "oauth", "Chạy các Actor để thu thập dữ liệu web.", "Run Actors to scrape and collect web data.", "97D700"),
    _s("huggingface", "Hugging Face", "https://huggingface.co/mcp", "data", "open", "Tìm model, dataset và Space trên Hugging Face.", "Search models, datasets and Spaces on Hugging Face.", "FFD21E"),
    _s("alphavantage", "Alpha Vantage", "https://mcp.alphavantage.co/mcp", "data", "oauth", "Dữ liệu chứng khoán, ngoại hối và tiền mã hóa.", "Stock, forex and crypto market data.", "1A56DB"),
    # --- Tim kiem va tai lieu
    _s("exa", "Exa", "https://mcp.exa.ai/mcp", "search", "open", "Tìm kiếm web bằng AI, không cần đăng nhập.", "AI-powered web search. No sign-in needed.", "1F40ED"),
    _s("firecrawl", "Firecrawl", "https://mcp.firecrawl.dev/mcp", "search", "open", "Đọc và thu thập nội dung trang web thành văn bản sạch.", "Read and crawl web pages into clean text.", "FF6B35"),
    _s("tavily", "Tavily", "https://mcp.tavily.com/mcp", "search", "oauth", "Tìm kiếm web được tối ưu cho agent.", "Web search tuned for agents.", "5B6CFF"),
    # --- Cong viec va cong tac
    _s("notion", "Notion", "https://mcp.notion.com/mcp", "work", "oauth", "Đọc và ghi trang, cơ sở dữ liệu trong Notion.", "Read and write pages and databases in Notion.", "000000"),
    _s("linear", "Linear", "https://mcp.linear.app/mcp", "work", "oauth", "Xem và tạo issue, project trong Linear.", "View and create issues and projects in Linear.", "5E6AD2"),
    _s("asana", "Asana", "https://mcp.asana.com/v2/mcp", "work", "oauth", "Quản lý công việc và dự án trong Asana.", "Manage tasks and projects in Asana.", "F06A6A"),
    _s("atlassian", "Atlassian", "https://mcp.atlassian.com/v1/mcp", "work", "oauth", "Jira và Confluence: tìm, đọc, tạo issue và trang.", "Jira and Confluence: search, read and create issues and pages.", "0052CC"),
    _s("clickup", "ClickUp", "https://mcp.clickup.com/mcp", "work", "oauth", "Quản lý task, danh sách và tài liệu trong ClickUp.", "Manage tasks, lists and docs in ClickUp.", "7B68EE"),
    _s("monday", "monday.com", "https://mcp.monday.com/mcp", "work", "oauth", "Quản lý bảng và mục công việc trên monday.com.", "Manage boards and items on monday.com.", "FF3D57"),
    _s("airtable", "Airtable", "https://mcp.airtable.com/mcp", "work", "oauth", "Đọc và ghi bản ghi trong các base Airtable.", "Read and write records in Airtable bases.", "18BFFF"),
    _s("todoist", "Todoist", "https://ai.todoist.net/mcp", "work", "oauth", "Quản lý việc cần làm trong Todoist.", "Manage your to-dos in Todoist.", "E44332"),
    _s("miro", "Miro", "https://mcp.miro.com", "work", "oauth", "Đọc và tạo nội dung trên bảng Miro.", "Read and create content on Miro boards.", "FFD02F"),
    _s("fireflies", "Fireflies", "https://api.fireflies.ai/mcp", "work", "oauth", "Tìm trong bản ghi và tóm tắt các cuộc họp.", "Search meeting transcripts and summaries.", "7C3AED"),
    _s("granola", "Granola", "https://mcp.granola.ai/mcp", "work", "oauth", "Truy cập ghi chú cuộc họp trong Granola.", "Access meeting notes in Granola.", "5CAB2A"),
    _s("zapier", "Zapier", "https://mcp.zapier.com/api/mcp/mcp", "work", "oauth", "Kích hoạt các hành động trong hàng nghìn ứng dụng qua Zapier.", "Trigger actions across thousands of apps through Zapier.", "FF4F00"),
    # --- Thiet ke va website
    _s("figma", "Figma", "https://mcp.figma.com/mcp", "design", "oauth", "Ngữ cảnh thiết kế, Code Connect và ghi vào canvas trong Figma (OAuth DCR).", "Design context, Code Connect and write-to-canvas in Figma (OAuth DCR).", "F24E1E"),
    _s("canva", "Canva", "https://mcp.canva.com/mcp", "design", "oauth", "Tạo slide, tìm, đọc và chỉnh thiết kế trong Canva.", "Create slides, find, read and edit designs in Canva.", "00C4CC"),
    _s("webflow", "Webflow", "https://mcp.webflow.com/mcp", "design", "oauth", "Quản lý site, trang và CMS của Webflow.", "Manage Webflow sites, pages and CMS.", "146EF5"),
    _s("wix", "Wix", "https://mcp.wix.com/mcp", "design", "oauth", "Quản lý site và cửa hàng trên Wix.", "Manage sites and stores on Wix.", "0C6EFC"),
    # --- Kinh doanh va thanh toan
    _s("stripe", "Stripe", "https://mcp.stripe.com", "biz", "oauth", "Xem khách hàng, thanh toán và hóa đơn trên Stripe.", "View customers, payments and invoices on Stripe.", "635BFF"),
    _s("paypal", "PayPal", "https://mcp.paypal.com/mcp", "biz", "oauth", "Quản lý giao dịch và hóa đơn trên PayPal.", "Manage transactions and invoices on PayPal.", "003087"),
    _s("square", "Square", "https://mcp.squareup.com/sse", "biz", "oauth", "Quản lý bán hàng, khách hàng và kho trên Square.", "Manage sales, customers and inventory on Square.", "3E4348", transport="sse"),
    _s("intercom", "Intercom", "https://mcp.intercom.com/mcp", "biz", "oauth", "Xem hội thoại và liên hệ khách hàng trong Intercom.", "View conversations and contacts in Intercom.", "6AFDEF"),
    _s("ramp", "Ramp", "https://mcp.ramp.com/mcp", "biz", "oauth", "Xem chi tiêu, thẻ và hóa đơn trên Ramp.", "View spend, cards and bills on Ramp.", "F4D03F"),
    # --- Them tu danh sach plugin chinh thuc (da thu: oauth = kham pha + dang ky client dong thanh cong, open = ket noi va liet ke duoc cong cu)
    _s("buildkite", "Buildkite", "https://mcp.buildkite.com/mcp", "dev", "oauth", "Xem pipeline, build và kết quả test trên Buildkite.", "CI/CD pipelines, builds and test results from Buildkite.", "14CC80"),
    _s("betterstack", "Better Stack", "https://mcp.betterstack.com", "dev", "oauth", "Xem log, uptime, sự cố và trang trạng thái trên Better Stack.", "Logs, uptime monitors, incidents and status pages on Better Stack.", "0EA5E9"),
    _s("grafana", "Grafana", "https://mcp.grafana.com/mcp", "dev", "oauth", "Truy vấn metric, log, dashboard và cảnh báo trên Grafana.", "Query metrics, logs, dashboards and alerts on Grafana.", "F46800"),
    _s("globalping", "Globalping", "https://mcp.globalping.dev/mcp", "dev", "oauth", "Ping, traceroute, DNS và kiểm tra HTTP từ nhiều nơi trên thế giới.", "Ping, traceroute, DNS and HTTP tests from global probes.", "17BEBB"),
    _s("aws-knowledge", "AWS Knowledge", "https://knowledge-mcp.global.api.aws", "search", "open", "Tài liệu AWS chính thức, tham chiếu API và thực hành tốt, không cần đăng nhập.", "Official AWS docs, API references and best practices. No sign-in needed.", "FF9900"),
    _s("alltrails", "AllTrails", "https://www.alltrails.com/mcp", "search", "open", "Tìm đường mòn đi bộ, thời tiết và chi tiết tuyến, không cần đăng nhập.", "Find hiking trails, weather and route details. No sign-in needed.", "428A13"),
    _s("amplitude", "Amplitude", "https://mcp.amplitude.com/mcp", "data", "oauth", "Xem biểu đồ, dashboard, thí nghiệm và feature flag trên Amplitude.", "Charts, dashboards, experiments and flags on Amplitude.", "1E61F0"),
    _s("cloudinary", "Cloudinary", "https://asset-management.mcp.cloudinary.com/mcp", "design", "oauth", "Tải lên, tìm kiếm và biến đổi ảnh, video trên Cloudinary.", "Upload, search and transform media assets on Cloudinary.", "3448C5"),
    _s("clay", "Clay", "https://api.clay.com/v3/mcp", "biz", "oauth", "Nghiên cứu khách hàng tiềm năng và làm giàu dữ liệu bán hàng với Clay.", "Sales research and enrichment workflows with Clay.", "F2C94C"),
    _s("close", "Close", "https://mcp.close.com/mcp", "biz", "oauth", "CRM bán hàng: lead, cơ hội, cuộc gọi và email trong Close.", "Sales CRM: leads, opportunities, calls and emails in Close.", "2B7DF7"),
    _s("shopify", "Shopify", "https://mcp.shopify.com/mcp", "biz", "open", "Công cụ cho cửa hàng Shopify: danh mục mẫu, gợi ý tên miền và sản phẩm số.", "Shopify store tools: mock catalogs, domain ideas and digital products.", "7AB55C"),
    _s("godaddy", "GoDaddy Domains", "https://api.godaddy.com/v1/domains/mcp", "biz", "open", "Gợi ý tên miền và kiểm tra tên miền còn trống, không cần đăng nhập.", "Domain suggestions and availability checks. No sign-in needed.", "1BDBDB"),
    # --- Tri tue nhan tao va mo hinh (Hermes AI)
    _s("anthropic-tools", "Anthropic Compute", "https://api.anthropic.com/mcp", "ai", "oauth", "Bộ công cụ Computer Use và thực thi mã nâng cao của Anthropic.", "Anthropic Computer Use and advanced code execution tools.", "D97706"),
    _s("memory-graph", "Knowledge Graph Memory", "https://memory.mcp.run/mcp", "ai", "open", "Đồ thị tri thức ngữ cảnh dài hạn cho trợ lý AI cá nhân.", "Long-term graph memory and knowledge entity connections.", "8B5CF6"),
    _s("replicate", "Replicate", "https://mcp.replicate.com", "ai", "oauth", "Chạy hàng nghìn mô hình AI sinh ảnh, video và xử lý giọng nói.", "Run open-source AI models for image, video and speech generation.", "000000"),
    # --- Bao mat va an toan (Hermes Security)
    _s("shodan", "Shodan Intelligence", "https://api.shodan.io/mcp", "sec", "token", "Quét thiết bị kết nối mạng, phát hiện lỗ hổng và cổng mở.", "Scan Internet-connected devices, detect CVEs and open ports.", "C93B2B", token=SHODAN_TOKEN),
    _s("virustotal", "VirusTotal", "https://www.virustotal.com/api/v3/mcp", "sec", "open", "Phân tích mã độc tập tin, kiểm tra URL và địa chỉ IP độc hại.", "Analyze suspicious files, URLs and malicious IP addresses.", "3949AB"),
    _s("onepassword", "1Password", "https://mcp.1password.com", "sec", "oauth", "Truy xuất mật khẩu, API key và credential an toàn từ vault.", "Retrieve credentials and secrets safely from 1Password vaults.", "0A85EA"),
    # --- Truyen thong va mang xa hoi (Hermes Media)
    _s("twitter", "X (Twitter)", "https://api.x.com/mcp", "media", "oauth", "Đăng bài viết, theo dõi xu hướng và phân tích tương tác trên X.", "Post tweets, monitor trending topics and analytics on X.", "000000"),
    _s("youtube", "YouTube Data", "https://youtube.googleapis.com/mcp", "media", "open", "Tra cứu video, lấy transcript phụ đề và thống kê kênh YouTube.", "Search videos, fetch transcripts and inspect channel statistics.", "FF0000"),
    _s("zotero", "Zotero Research", "https://zotero.mcp.run/mcp", "media", "open", "Quản lý thư viện tài liệu, trích dẫn chuẩn học thuật và PDF.", "Manage citation libraries, scholarly papers and PDF annotations.", "CC292B"),
    # --- Lap trinh, ha tang va tim kiem bo sung (Hermes Developer Tools)
    _s("docker", "Docker Engine", "https://mcp.docker.com/mcp", "dev", "open", "Quản lý container, image, volumes và Docker Compose.", "Manage containers, images, volumes and Docker Compose.", "2496ED"),
    _s("kubernetes", "Kubernetes", "https://mcp.kubernetes.io/mcp", "dev", "open", "Kiểm tra pod, deployment, service và log cụm Kubernetes.", "Inspect pods, deployments, services and k8s logs.", "326CE5"),
    _s("puppeteer", "Puppeteer Browser", "https://puppeteer.mcp.run/mcp", "dev", "open", "Duyệt web tự động, cào dữ liệu và chụp ảnh màn hình.", "Headless web browsing, web scraping and screenshots.", "00D8A2"),
    _s("brave-search", "Brave Search", "https://api.search.brave.com/mcp", "search", "token", "Tìm kiếm web độc lập, chỉ mục riêng và bảo vệ quyền riêng tư.", "Independent web search, private indexing with zero tracking.", "FB542B", token=BRAVE_TOKEN),
    _s("perplexity", "Perplexity AI", "https://api.perplexity.ai/mcp", "search", "token", "Tìm kiếm và tổng hợp câu trả lời thông minh từ web.", "AI-powered web search and answer synthesis.", "1FB8CD", token=PERPLEXITY_TOKEN),
    _s("arxiv", "arXiv Research", "https://arxiv.mcp.run/mcp", "search", "open", "Tìm kiếm, đọc tóm tắt và tải bài báo khoa học từ arXiv.", "Search, read abstracts and download research papers from arXiv.", "B31B1B"),
    _s("slack", "Slack", "https://slack.com/api/mcp", "work", "token", "Gửi tin nhắn, đọc kênh và trao đổi nhóm trong Slack.", "Send messages, read channels and collaborate in Slack.", "4A154B", token=SLACK_TOKEN),
    _s("discord", "Discord", "https://discord.com/api/mcp", "work", "token", "Tương tác server, gửi thông báo và quản lý bot Discord.", "Interact with servers, send notifications and manage Discord bots.", "5865F2", token=DISCORD_TOKEN),
    _s("obsidian", "Obsidian Vault", "https://obsidian.mcp.run/mcp", "work", "open", "Đọc, tạo và liên kết các ghi chú trong Obsidian Vault.", "Read, create and link notes in your Obsidian Vault.", "7C3AED"),
]


def catalog() -> dict:
    return {"groups": GROUPS, "services": SERVICES}
