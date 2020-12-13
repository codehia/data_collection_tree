class Node(object):

    """Docstring for Node. """

    def __init__(self, value, metrics={"webrq": 0, "timespent": 0}, children=[]):
        """
        :Docstring for Node.: TODO

        """
        self.dim_type = value.get("key")
        self.dim_value = value.get("value")
        self.metrics = metrics
        self.children = children

    def __str__(self) -> str:
        chil = [ch.dim_value for ch in self.children]
        return f"{self.dim_type} {self.dim_value} {str(self.metrics)} {chil}"


def create_base_tree(root):
    country_level = [[{"key": "country", "value": "IN"}, {"webreq": 0, "timespent": 0}]]
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


def show_tree(root):
    queue = [root] if root else []
    while queue:
        next_level = []
        for node in queue:
            print(node)
            if node.children:
                next_level.extend([child for child in node.children])
        queue = next_level


def insert_nodes(root, dimensions, metrics):
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
                                    device.metrics["webreq"] += metrics.get("webreq")
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
                    device_node = Node(
                        {"key": "device", "value": dimensions.get("device")},
                        {
                            "webreq": metrics.get("webreq"),
                            "timespent": metrics.get("timespent"),
                        },
                    )
                    root.children.append(country_node)
                    country_node.children.append(device_node)
                    root.metrics["webreq"] += metrics.get("webreq")
                    root.metrics["timespent"] += metrics.get("timespent")
                    country_not_found_flag = False
                    next_level = []
                    queue = next_level
                    break
        queue = next_level


def insert_data(data, root):
    dimensions = {dim.get("key"): dim.get("val") for dim in data.get("dim")}
    metrics = {
        metrics.get("key"): metrics.get("val") for metrics in data.get("metrics")
    }
    insert_nodes(root, dimensions, metrics)


def main():
    root = Node({"key": "root", "value": "total"}, {"webreq": 0, "timespent": 0})
    create_base_tree(root)
    show_tree(root)
    data = {
        "dim": [{"key": "device", "val": "mobile"}, {"key": "country", "val": "IN"}],
        "metrics": [{"key": "webreq", "val": 70}, {"key": "timespent", "val": 30}],
    }
    insert_data(data, root)
    data = {
        "dim": [{"key": "device", "val": "mobile"}, {"key": "country", "val": "IN"}],
        "metrics": [{"key": "webreq", "val": 70}, {"key": "timespent", "val": 30}],
    }
    insert_data(data, root)
    data = {
        "dim": [{"key": "device", "val": "mobile"}, {"key": "country", "val": "US"}],
        "metrics": [{"key": "webreq", "val": 70}, {"key": "timespent", "val": 30}],
    }
    insert_data(data, root)
    show_tree(root)


if __name__ == "__main__":
    main()
