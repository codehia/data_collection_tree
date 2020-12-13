from fastapi import status


class Node(object):
    def __init__(self, value, metrics={"webrq": 0, "timespent": 0}, children=[]):
        self.dim_type = value.get("key")
        self.dim_value = value.get("value")
        self.metrics = metrics
        self.children = children

    def __str__(self) -> str:
        children = ",".join([ch.dim_value for ch in self.children])
        return f"{self.dim_type} {self.dim_value} {str(self.metrics)} {children}"


class Tree(object):
    def __init__(self):
        self.root = self._create_base_tree()

    def _create_base_tree(self):
        root = Node({"key": "root", "value": "total"}, {"webreq": 0, "timespent": 0})
        country_level = [
            [{"key": "country", "value": "IN"}, {"webreq": 0, "timespent": 0}]
        ]
        root.children = [Node(value, metrics) for value, metrics in country_level]
        device_level = [
            [{"key": "device", "value": "mobile"}, {"webreq": 0, "timespent": 0}],
            [{"key": "device", "value": "web"}, {"webreq": 0, "timespent": 0}],
        ]
        for country in root.children:
            children = []
            for value, metrics in device_level:
                children.append(Node(value, metrics))
            country.children = children
        return root

    def _insert_nodes(self, root, dimensions, metrics):
        queue = [root] if root else []
        country_not_found_flag = True
        device_not_found_flag = True
        while queue:
            country_not_found_flag = True
            device_not_found_flag = True
            next_level = []
            country_level = []
            for node in queue:
                if node.dim_type == "root":
                    country_level = [child for child in node.children]
                    for country in country_level:
                        if dimensions.get("country") == country.dim_value:
                            country_not_found_flag = False
                            country.metrics["webreq"] += metrics.get("webreq")
                            country.metrics["timespent"] += metrics.get("timespent")
                            root.metrics["webreq"] += metrics.get("webreq")
                            root.metrics["timespent"] += metrics.get("timespent")
                            if country.children:
                                device_level = [child for child in country.children]
                                for device in device_level:
                                    if device.dim_value == dimensions.get("device"):
                                        device_not_found_flag = False
                                        device.metrics["webreq"] += metrics.get(
                                            "webreq"
                                        )
                                        device.metrics["timespent"] += metrics.get(
                                            "timespent"
                                        )
                                        next_level = []
                                        queue = next_level
                                        break
                                if device_not_found_flag:
                                    device_not_found_flag = False
                                    country.children.append(
                                        Node(
                                            {
                                                "key": "device",
                                                "value": dimensions.get("device"),
                                            },
                                            {
                                                "webreq": metrics.get("webreq"),
                                                "timespent": metrics.get("timespent"),
                                            },
                                        )
                                    )
                                    next_level = []
                                    queue = next_level
                                    break
                            else:
                                country.children.append(
                                    Node(
                                        {
                                            "key": "device",
                                            "value": dimensions.get("device"),
                                        },
                                        {
                                            "webreq": metrics.get("webreq"),
                                            "timespent": metrics.get("timespent"),
                                        },
                                    )
                                )
                                next_level = []
                                queue = next_level
                                break
                    if country_not_found_flag:
                        country_node = Node(
                            {"key": "country", "value": dimensions.get("country")},
                            {
                                "webreq": metrics.get("webreq"),
                                "timespent": metrics.get("timespent"),
                            },
                        )
                        country_node.children = [
                            Node(
                                {"key": "device", "value": dimensions.get("device")},
                                {
                                    "webreq": metrics.get("webreq"),
                                    "timespent": metrics.get("timespent"),
                                },
                            )
                        ]
                        root.children.append(country_node)
                        root.metrics["webreq"] += metrics.get("webreq")
                        root.metrics["timespent"] += metrics.get("timespent")
                        country_not_found_flag = False
                        next_level = []
                        queue = next_level
                        break
            queue = next_level

    def insert_data(self, data):
        dimensions = {dim.get("key"): dim.get("val") for dim in data.get("dim")}
        metrics = {
            metrics.get("key"): metrics.get("val") for metrics in data.get("metrics")
        }
        self._insert_nodes(self.root, dimensions, metrics)
        return status.HTTP_200_OK

    def fetch_data(self, key, value):
        response = None
        queue = [self.root] if self.root else []
        while queue:
            next_level = []
            for node in queue:
                if node.dim_value == value:
                    response = {
                        "dim": [{"key": key, "val": node.dim_value}],
                        "metrics": [
                            {"key": "webreq", "val": node.metrics.get("webreq")},
                            {"key": "timespent", "val": node.metrics.get("timespent")},
                        ],
                    }
                    return response, status.HTTP_200_OK
                if node.children:
                    next_level.extend([child for child in node.children])
            queue = next_level

