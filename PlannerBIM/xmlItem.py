from os import remove
from tracemalloc import start


class XmlItem():
    """XmlItem: Class to hold all useful informations for items of XML file.

    This is used to create the 3D objects in freecad from the imported XML file.
    """
    
    def __init__(self, item_id: str, name: str,
                 start_time: str, finish_time: str, summary: str,
                 outline_number: str, predecessor_id: str=None) -> None:
        self.item_id = item_id
        self.name = self.remove_accents(name.lower())
        self.start_time = start_time
        self.finish_time = finish_time
        self.predecessor_id = predecessor_id

        self.item_type = self.identify_item_type(summary, outline_number)

    def identify_item_type(self, summary: str, outline_number: str) -> str:
        """identify_item_type Identify if the item is Schedule, Title or Task
        
        The rule:
            summary = 0 --> type is Task
            summary = 1
                outline_number = 1 (single number) --> type is Schedule
                outline_number = 1.1 (two number with dot) --> type is Title

        Args:
            summary (str): summary number to identify if Task or other
            outline_number (str): Number to identify if Schedule or Title

        Returns:
            str: Type identified.
        """
        if summary == "0":
            return "TASK"
        else:
            if "." in outline_number:
                return "TITLE"
            else:
                return "SCHEDULE"

    def remove_accents(self, text: str) -> str:
        """remove_accents Remove accents from string

        Args:
            text (str): string to remove accents

        Returns:
            str: clean string
        """
        accents_string = "áéíóúàèìòùäëïöüâêîôûãẽĩõũç"
        no_accents     = "aeiouaeiouaeiouaeiouaeiouc"
        repl = str.maketrans(accents_string, no_accents)
        return text.translate(repl)
