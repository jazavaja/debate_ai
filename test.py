from models.debate_config import DebateConfig
from models.debater import Debater
from models.debate_project import DebateProject
from utils.file_handler import FileHandler
from core.debate_engine import DebateTurn

def demo_save_load():
    cfg = DebateConfig(
        topic="نمونه موضوع",
        debater1=Debater(name="طرف اول", prompt="توضیحات طرف اول"),
        debater2=Debater(name="طرف دوم", prompt="توضیحات طرف دوم"),
        moderator=Debater(name="مجری", prompt="توضیحات مجری", role="moderator"),
        max_turns=3
    )
    project = DebateProject(config=cfg)
    project.turns.append(DebateTurn(speaker=cfg.debater1.name, content="اولین استدلال...", turn_number=1))
    project.turns.append(DebateTurn(speaker=cfg.debater2.name, content="پاسخ طرف دوم...", turn_number=2))
    project.conclusion = "نتیجه‌گیری نمونه"
    json_path = FileHandler.save_project_json(project, "debates/demo_project.json")
    print("Saved:", json_path)
    loaded = FileHandler.load_project_json(json_path)
    print("Loaded topic:", loaded.config.topic)
    txt_path = FileHandler.save_project_text(loaded, "debates/demo_project.txt")
    print("Saved text:", txt_path)

if __name__ == '__main__':
    demo_save_load()