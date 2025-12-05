"""ProjectManager: project filesystem operations extracted from app.py"""
from pathlib import Path
import json
from datetime import datetime
import shutil
import time
import hashlib


class ProjectManager:
    def __init__(self):
        self.projects_dir = Path("projects")
        self.projects_dir.mkdir(exist_ok=True)
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)
    
    def list_projects(self):
        """列出所有项目"""
        projects = []
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                config_file = project_dir / "project.json"
                html_file = project_dir / "index.html"
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                        
                        # 检查HTML文件是否存在
                        has_html = html_file.exists()
                        
                        projects.append({
                            "name": project_dir.name,
                            "config": config,
                            "path": project_dir,
                            "has_html": has_html,
                            "html_path": html_file if has_html else None,
                            "last_modified": config.get('last_modified', ''),
                            "size": self.get_project_size(project_dir),
                            "page_count": self.get_page_count(project_dir),
                            "element_count": self.get_element_count(project_dir)
                        })
                    except Exception as e:
                        print(f"Error loading project {project_dir.name}: {e}")
                        continue
        # 按最后修改时间排序
        return sorted(projects, key=lambda x: x["config"].get("last_modified", ""), reverse=True)
    
    def get_project_size(self, project_path):
        """计算项目大小"""
        total_size = 0
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
    
    def get_page_count(self, project_path):
        """获取页面数量"""
        structure_file = project_path / "structure.json"
        if structure_file.exists():
            try:
                with open(structure_file, 'r', encoding='utf-8') as f:
                    structure = json.load(f)
                return len(structure.get('pages', [])) + 1  # 加封面页
            except:
                return 0
        return 0
    
    def get_element_count(self, project_path):
        """获取元素数量"""
        structure_file = project_path / "structure.json"
        if structure_file.exists():
            try:
                with open(structure_file, 'r', encoding='utf-8') as f:
                    structure = json.load(f)
                
                count = 0
                # 封面页元素
                if 'content' in structure.get('cover_page', {}):
                    count += len(structure['cover_page']['content'])
                # 其他页面元素
                for page in structure.get('pages', []):
                    if 'content' in page:
                        count += len(page['content'])
                return count
            except:
                return 0
        return 0
    
    def format_size(self, size_bytes):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"
    
    def create_project(self, name, description=""):
        """创建新项目"""
        # 验证项目名
        if not name or not name.strip():
            return False, "项目名称不能为空"
        
        # 清理项目名
        import re
        clean_name = re.sub(r'[^\w\s-]', '', name.strip())
        clean_name = re.sub(r'[-\s]+', '-', clean_name)
        
        if not clean_name:
            return False, "项目名称无效"
        
        project_path = self.projects_dir / clean_name
        if project_path.exists():
            return False, "项目已存在"
        
        try:
            # 创建项目目录结构
            project_path.mkdir()
            (project_path / "assets").mkdir(exist_ok=True)
            (project_path / "static").mkdir(exist_ok=True)
            (project_path / "backups").mkdir(exist_ok=True)
            
            # 项目配置
            config = {
                "name": clean_name,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "author": "用户",
                "version": "1.0.0",
                "settings": {
                    "theme": "light",
                    "animations": True,
                    "sidebar_collapsible": True,
                    "show_back_to_top": True,
                    "enable_comments": False,
                    "show_word_count": True,
                    "auto_save": True,
                    "font_family": "Inter, 'Microsoft YaHei', sans-serif",
                    "primary_color": "#667eea",
                    "secondary_color": "#764ba2"
                }
            }
            
            # 项目结构
            structure = {
                "title": clean_name,
                "description": description,
                "cover_page": {
                    "id": "cover",
                    "title": "欢迎页面",
                    "type": "page",
                    "content": [
                        {
                            "id": "welcome_heading",
                            "type": "heading",
                            "text": f"欢迎来到{clean_name}",
                            "level": 1,
                            "color": "#2d3748",
                            "align": "center"
                        },
                        {
                            "id": "welcome_text",
                            "type": "paragraph",
                            "text": f"这是{clean_name}的开始页面。\n请使用左侧目录添加或编辑内容。",
                            "color": "#4a5568",
                            "background": "#ffffff",
                            "align": "center"
                        },
                        {
                            "id": "quick_start",
                            "type": "note",
                            "text": "提示：您可以随时编辑这个页面，添加您自己的内容",
                            "author": "系统提示",
                            "color": "#666666",
                            "background": "#f8f9fa"
                        }
                    ]
                },
                "pages": [],
                "config": config["settings"]
            }
            
            # 保存文件
            with open(project_path / "project.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            with open(project_path / "structure.json", 'w', encoding='utf-8') as f:
                json.dump(structure, f, ensure_ascii=False, indent=2)
            
            # 创建备份
            self.create_backup(clean_name, structure)
            
            return True, "项目创建成功"
            
        except Exception as e:
            # 清理失败的项目
            if project_path.exists():
                try:
                    shutil.rmtree(project_path)
                except:
                    pass
            return False, f"创建失败: {str(e)}"
    
    def load_project(self, name):
        """加载项目"""
        project_path = self.projects_dir / name
        if not project_path.exists():
            return False, "项目不存在"
        
        try:
            # 验证项目文件
            required_files = ["project.json", "structure.json"]
            for file in required_files:
                if not (project_path / file).exists():
                    return False, f"项目文件损坏: {file} 不存在"
            
            with open(project_path / "project.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            with open(project_path / "structure.json", 'r', encoding='utf-8') as f:
                structure = json.load(f)
            
            # 验证结构完整性
            if not self.validate_structure(structure):
                return False, "项目结构损坏，无法加载"
            
            # 检查是否需要升级
            structure = self.upgrade_structure(structure)
            
            return True, {
                "name": name,
                "config": config,
                "structure": structure,
                "path": project_path,
                "html_path": project_path / "index.html" if (project_path / "index.html").exists() else None
            }
            
        except json.JSONDecodeError as e:
            return False, f"项目文件格式错误: {str(e)}"
        except Exception as e:
            return False, f"加载失败: {str(e)}"
    
    def validate_structure(self, structure):
        """验证项目结构完整性"""
        if not isinstance(structure, dict):
            return False
        
        required_keys = ["title", "cover_page", "pages", "config"]
        for key in required_keys:
            if key not in structure:
                return False
        
        # 验证封面页
        if not isinstance(structure["cover_page"], dict):
            return False
        if "id" not in structure["cover_page"] or "title" not in structure["cover_page"]:
            return False
        
        # 验证页面列表
        if not isinstance(structure["pages"], list):
            return False
        
        # 验证配置
        if not isinstance(structure["config"], dict):
            return False
        
        return True
    
    def upgrade_structure(self, structure):
        """升级项目结构到最新版本"""
        # 检查版本
        if "version" not in structure:
            structure["version"] = "1.0"
        
        # 确保必要的字段存在
        if "config" not in structure:
            structure["config"] = {
                "theme": "light",
                "animations": True,
                "sidebar_collapsible": True,
                "show_back_to_top": True
            }
        
        # 确保封面页有content字段
        if "content" not in structure["cover_page"]:
            structure["cover_page"]["content"] = []
        
        # 确保所有页面有content字段
        for page in structure["pages"]:
            if "content" not in page:
                page["content"] = []
        
        return structure
    
    def create_backup(self, project_name, structure):
        """创建项目备份"""
        try:
            backup_dir = self.backup_dir / project_name
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"backup_{timestamp}.json"
            
            backup_data = {
                "timestamp": timestamp,
                "datetime": datetime.now().isoformat(),
                "structure": structure,
                "version": "2.0",
                "checksum": self.calculate_checksum(structure)
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            # 保留最近20个备份
            backups = list(backup_dir.glob("backup_*.json"))
            if len(backups) > 20:
                backups.sort()
                for old_backup in backups[:-20]:
                    try:
                        old_backup.unlink()
                    except:
                        pass
                        
        except Exception as e:
            print(f"Backup failed: {e}")
    
    def calculate_checksum(self, data):
        """计算数据校验和"""
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()
    
    def delete_project(self, name):
        """删除项目"""
        project_path = self.projects_dir / name
        if not project_path.exists():
            return False, "项目不存在"
        
        try:
            # 创建最终备份
            if (project_path / "structure.json").exists():
                with open(project_path / "structure.json", 'r', encoding='utf-8') as f:
                    structure = json.load(f)
                self.create_backup(name, structure)
            
            # 移动到回收站（临时目录）
            recycle_path = self.temp_dir / f"deleted_{name}_{int(time.time())}"
            shutil.move(project_path, recycle_path)
            
            # 删除备份目录
            backup_path = self.backup_dir / name
            if backup_path.exists():
                shutil.rmtree(backup_path)
            
            return True, "项目已移动到回收站"
            
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    def restore_project(self, name):
        """从回收站恢复项目"""
        # 查找回收站中的项目
        for item in self.temp_dir.iterdir():
            if item.name.startswith(f"deleted_{name}_"):
                try:
                    # 移回项目目录
                    project_path = self.projects_dir / name
                    shutil.move(item, project_path)
                    return True, "项目恢复成功"
                except Exception as e:
                    return False, f"恢复失败: {str(e)}"
        return False, "未找到要恢复的项目"
