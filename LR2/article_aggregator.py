def create_article(article_id, /, title, text, *, source, tags=None, **metadata):
    ochistka_zagolovka=' '.join(title.split())
    probeli_po_krayam=text.strip()
    if tags is None:
        tags=[]
    ochishen_tag=[]
    proverka_doub=set()
    for tag in tags:
        probel_i_registr=tag.strip().lower()
        if probel_i_registr!="" and probel_i_registr not in proverka_doub:
            ochishen_tag.append(probel_i_registr)
            proverka_doub.add(probel_i_registr)
    slovar={
        "id": article_id,
        "title": ochistka_zagolovka,
        "text": probeli_po_krayam,
        "source": source,
        "tags": ochishen_tag,
        "metadata": metadata,
    }

    return slovar






def make_pipeline(*functions):
    def pipeline(detal):
        result=detal
        for f in functions:
            result=f(result)
        return result
    return pipeline







def make_service_monitor(max_failures, /):
    successes = 0
    failures = 0
    consecutive_failures = 0

    def can_call():
        return consecutive_failures < max_failures

    def status():
        return {
            "successes": successes,
            "failures": failures,
            "consecutive_failures": consecutive_failures,
            "available": can_call(),
        }

    def record(success):
        nonlocal successes, failures, consecutive_failures
        if success:
            successes += 1
            consecutive_failures = 0
        else:
            failures += 1
            consecutive_failures += 1
        return can_call()

    def reset():
        nonlocal successes, failures, consecutive_failures
        successes = 0
        failures = 0
        consecutive_failures = 0
        return status()

    return {
        "record": record,
        "can_call": can_call,
        "status": status,
        "reset": reset,
    }





def build_application(sources, /, *, max_failures=3):
    
    sources_copy = dict(sources)
    monitors = {}
    for name in sources_copy:
        monitors[name] = make_service_monitor(max_failures)
    catalog = {}
    
   
    
    def fetch(source_name):
        monitor = monitors[source_name]
        
        
        if not monitor["can_call"]():
            return {
                "status": "blocked",
                "source": source_name,
                "received": 0,
                "added": 0,
                "updated": 0,
            }
        
        
        raw_articles = sources_copy[source_name]()
        
        
        if raw_articles is None:
            monitor["record"](False)
            return {
                "status": "unavailable",
                "source": source_name,
                "received": 0,
                "added": 0,
                "updated": 0,
            }
        
        
        monitor["record"](True)
        added = 0
        updated = 0
        
        for raw in raw_articles:
           
            metadata = {}
            for k, v in raw.items():
                if k not in ("id", "title", "text", "tags"):
                    metadata[k] = v
            
            
            statya = create_article(
                raw["id"],
                raw["title"],
                raw["text"],
                source=source_name,
                tags=raw.get("tags"),
                **metadata
            )
            
            
            if statya["id"] in catalog:
                updated += 1
            else:
                added += 1
            
            catalog[statya["id"]] = statya
        
        return {
            "status": "ok",
            "source": source_name,
            "received": len(raw_articles),
            "added": added,
            "updated": updated,
        }
    
    
    def list_articles():
        result = []
        for statya in catalog.values():
            kopiya = {
                "id": statya["id"],
                "title": statya["title"],
                "text": statya["text"],
                "source": statya["source"],
                "tags": list(statya["tags"]),
                "metadata": dict(statya["metadata"]),
            }
            result.append(kopiya)
        return result
    
    
    def search(query, source=None, tag=None):
        query_lower = query.lower()
        tag_lower = tag.strip().lower() if tag is not None else None
        result = []
        
        for statya in catalog.values():
            
            if source is not None and statya["source"] != source:
                continue
            
            
            if tag_lower is not None and tag_lower not in statya["tags"]:
                continue
            
            
            if query_lower != "":
                if query_lower not in statya["title"].lower() and \
                   query_lower not in statya["text"].lower():
                    continue
            
            
            kopiya = {
                "id": statya["id"],
                "title": statya["title"],
                "text": statya["text"],
                "source": statya["source"],
                "tags": list(statya["tags"]),
                "metadata": dict(statya["metadata"]),
            }
            result.append(kopiya)
        
        return result
    
    
    def stats():
        by_source = {}
        for name in sources_copy:
            by_source[name] = 0
        
        for statya in catalog.values():
            by_source[statya["source"]] += 1
        
        return {
            "total_articles": len(catalog),
            "by_source": by_source,
            "available_sources": tuple(sources_copy.keys()),
        }
    
    
    def source_status(source_name):
        return monitors[source_name]["status"]()
    
    
    def reset_source(source_name):
        return monitors[source_name]["reset"]()
    
    
    def available_commands():
        return ("fetch", "list", "search", "stats", "status", "reset", "commands")
    
    

    commands = {
        "fetch": fetch,
        "list": list_articles,
        "search": search,
        "stats": stats,
        "status": source_status,
        "reset": reset_source,
        "commands": available_commands,
    }

    def run(command, /, *args, **kwargs):
        func = commands[command]
        return func(*args, **kwargs)


    return run





