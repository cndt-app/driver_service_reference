from typing import Any

import json
import html


def make_result_script(rid: str, origin: str, secrets: dict[str, Any]) -> str:
    tpl = """
    <script type="text/javascript">
        (function() {{
            window.parent.postMessage({{
                'event': 'conduit:connect:complete',
                'rid': '{rid}',
                'payload': JSON.stringify({payload})
            }}, '{origin}')
        }})()
    </script>
    """

    return tpl.format(
        rid=html.escape(rid),
        origin=html.escape(origin),
        payload=json.dumps(secrets),
    )
