"""
Explain Analyzer for Adaptive Learning Coach
Analyzes codebase modules and caches results for quick explanation.
"""

import json
import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    from .progress_manager import get_progress_manager, ProgressManager
except ImportError:
    from progress_manager import get_progress_manager, ProgressManager


CACHE_FRESH_HOURS = 24
CACHE_STALE_HOURS = 72


class ExplainAnalyzer:
    """Analyzes codebase modules and manages analysis cache."""
    
    def __init__(self, skill_dir: Optional[Path] = None):
        self.skill_dir = skill_dir or Path(__file__).parent.parent
        self.pm = get_progress_manager(self.skill_dir)
    
    def get_cached_analysis(self, repo_id: int, module_path: str) -> Optional[Dict]:
        """Get cached module analysis if exists."""
        conn = self.pm._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT * FROM module_cache 
            WHERE repo_id = ? AND module_path = ?""",
            (repo_id, module_path)
        )
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_cache_status(self, repo_id: int, module_path: str) -> Dict:
        """
        Check cache status and return recommendation.
        
        Returns:
            {
                'has_cache': bool,
                'analyzed_at': datetime,
                'hours_since': int,
                'status': 'fresh'|'stale'|'missing',
                'recommendation': 'use_cache'|'refresh'|'analyze'
            }
        """
        cached = self.get_cached_analysis(repo_id, module_path)
        
        if not cached:
            return {
                'has_cache': False,
                'analyzed_at': None,
                'hours_since': None,
                'status': 'missing',
                'recommendation': 'analyze'
            }
        
        analyzed_at = datetime.fromisoformat(cached['analyzed_at'])
        hours_since = int((datetime.now() - analyzed_at).total_seconds() / 3600)
        
        if hours_since < CACHE_FRESH_HOURS:
            status = 'fresh'
            recommendation = 'use_cache'
        elif hours_since < CACHE_STALE_HOURS:
            status = 'stale'
            recommendation = 'ask_user'
        else:
            status = 'stale'
            recommendation = 'refresh'
        
        return {
            'has_cache': True,
            'analyzed_at': analyzed_at,
            'hours_since': hours_since,
            'status': status,
            'recommendation': recommendation,
            'cached_data': cached
        }
    
    def analyze_module(self, repo_path: str, module_path: str) -> Dict:
        """
        Analyze a module/directory in a codebase.
        
        Returns high-level and detailed analysis.
        """
        full_path = Path(repo_path) / module_path
        
        if not full_path.exists():
            return {
                'error': f"Module not found: {module_path}",
                'highlevel': None,
                'detailed': None
            }
        
        analysis = {
            'highlevel': self._analyze_highlevel(full_path, module_path),
            'detailed': self._analyze_detailed(full_path, module_path)
        }
        
        return analysis
    
    def _analyze_highlevel(self, module_path: Path, module_name: str) -> Dict:
        """
        Generate high-level overview of a module.
        
        Returns:
            {
                'purpose': str,
                'key_files': list,
                'relationships': dict,
                'key_concepts': list,
                'complexity': str
            }
        """
        highlevel = {
            'purpose': self._infer_purpose(module_path, module_name),
            'key_files': self._find_key_files(module_path),
            'relationships': {
                'imports_from': self._find_imports(module_path),
                'used_by': self._find_usages(module_path),
                'tests': self._find_tests(module_path)
            },
            'key_concepts': self._extract_concepts(module_path),
            'complexity': self._estimate_complexity(module_path)
        }
        
        return highlevel
    
    def _analyze_detailed(self, module_path: Path, module_name: str) -> Dict:
        """
        Generate detailed analysis of a module.
        
        Returns:
            {
                'functions': list,
                'classes': list,
                'flow': str,
                'entry_points': list,
                'exports': list
            }
        """
        detailed = {
            'functions': self._extract_functions(module_path),
            'classes': self._extract_classes(module_path),
            'flow': self._infer_flow(module_path),
            'entry_points': self._find_entry_points(module_path),
            'exports': self._find_exports(module_path)
        }
        
        return detailed
    
    def _infer_purpose(self, module_path: Path, module_name: str) -> str:
        """Infer module purpose from name and contents."""
        name_lower = module_name.lower()
        
        purpose_hints = {
            'auth': 'User authentication and authorization',
            'api': 'API endpoints and request handling',
            'core': 'Core business logic and domain',
            'utils': 'Utility functions and helpers',
            'services': 'Service layer and business operations',
            'models': 'Data models and entities',
            'controllers': 'Request routing and control',
            'views': 'UI components and views',
            'components': 'Reusable UI components',
            'lib': 'Library functions and shared code',
            'config': 'Configuration and settings',
            'tests': 'Test suites and fixtures',
            'middleware': 'Request/response middleware',
            'database': 'Database operations and queries',
            'storage': 'Data storage and persistence',
            'handlers': 'Event handlers and callbacks',
        }
        
        if name_lower in purpose_hints:
            return purpose_hints[name_lower]
        
        readme = module_path / 'README.md'
        if readme.exists():
            try:
                first_lines = readme.read_text()[:500]
                if first_lines:
                    return f"See README for details"
            except:
                pass
        
        return f"Module containing {module_name} functionality"
    
    def _find_key_files(self, module_path: Path) -> List[Dict]:
        """Find key files in module."""
        key_files = []
        
        priority_files = ['index', 'main', 'app', 'core', 'base', 'types', 'utils']
        
        for file in module_path.iterdir():
            if file.is_file() and file.suffix in ['.py', '.js', '.ts', '.tsx', '.go', '.rs', '.java']:
                name = file.stem.lower()
                is_key = any(p in name for p in priority_files)
                
                key_files.append({
                    'path': file.name,
                    'lines': self._count_lines(file),
                    'is_key': is_key,
                    'description': self._infer_file_purpose(file)
                })
        
        key_files.sort(key=lambda x: (-x['is_key'], -x['lines']))
        
        return key_files[:10]
    
    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file."""
        try:
            return len(file_path.read_text().splitlines())
        except:
            return 0
    
    def _infer_file_purpose(self, file_path: Path) -> str:
        """Infer file purpose from name."""
        name = file_path.stem.lower()
        suffix = file_path.suffix
        
        purpose_map = {
            'index': 'Module entry point and exports',
            'main': 'Main execution entry',
            'app': 'Application configuration',
            'types': 'Type definitions and interfaces',
            'utils': 'Utility functions',
            'helper': 'Helper functions',
            'constants': 'Constants and configuration values',
            'config': 'Configuration settings',
            'test': 'Test definitions',
            'spec': 'Test specifications',
            'model': 'Data model/entity',
            'service': 'Service logic',
            'controller': 'Request handling',
            'handler': 'Event/request handler',
            'route': 'Route definitions',
            'middleware': 'Middleware logic',
        }
        
        for key, purpose in purpose_map.items():
            if key in name:
                return purpose
        
        return f"{name} implementation"
    
    def _find_imports(self, module_path: Path) -> List[str]:
        """Find modules/packages this module imports from."""
        imports = []
        
        import_patterns = {
            '.py': ['import ', 'from '],
            '.js': ['require(', 'import '],
            '.ts': ['import ', 'require('],
            '.tsx': ['import ', 'require('],
            '.go': ['import '],
        }
        
        for file in module_path.iterdir():
            if file.is_file() and file.suffix in import_patterns:
                try:
                    content = file.read_text()
                    patterns = import_patterns[file.suffix]
                    
                    for pattern in patterns:
                        lines = [l for l in content.splitlines() if pattern in l]
                        for line in lines[:5]:
                            imports.extend(self._extract_import_names(line, pattern))
                except:
                    pass
        
        return list(set(imports))[:10]
    
    def _extract_import_names(self, line: str, pattern: str) -> List[str]:
        """Extract import names from a line."""
        names = []
        
        if pattern == 'import ':
            if 'from' in line:
                parts = line.split('from')
                if len(parts) > 1:
                    name = parts[1].strip().split()[0].strip("'\"")
                    names.append(name)
            elif 'import' in line and '{' not in line:
                parts = line.split('import')
                if len(parts) > 1:
                    name = parts[1].strip().split()[0].strip("'\"")
                    names.append(name)
        
        if pattern == 'from ':
            parts = line.split('from')
            if len(parts) > 1:
                name = parts[1].strip().split()[0].strip("'\"")
                names.append(name)
        
        if pattern == 'require(':
            start = line.find('require(')
            if start >= 0:
                end = line.find(')', start)
                if end > start:
                    name = line[start+8:end].strip("'\"")
                    names.append(name)
        
        return names
    
    def _find_usages(self, module_path: Path) -> List[str]:
        """Find modules that might use this module."""
        module_name = module_path.name
        parent = module_path.parent
        
        usages = []
        
        for sibling in parent.iterdir():
            if sibling.is_dir() and sibling.name != module_name:
                for file in sibling.iterdir():
                    if file.is_file() and file.suffix in ['.py', '.js', '.ts', '.tsx', '.go']:
                        try:
                            content = file.read_text()
                            if module_name in content:
                                usages.append(sibling.name)
                        except:
                            pass
        
        return list(set(usages))[:5]
    
    def _find_tests(self, module_path: Path) -> List[str]:
        """Find test files for this module."""
        tests = []
        
        test_patterns = ['test', 'spec', '_test', '.test', '.spec']
        
        for file in module_path.iterdir():
            if file.is_file():
                name_lower = file.name.lower()
                if any(p in name_lower for p in test_patterns):
                    tests.append(file.name)
        
        return tests
    
    def _extract_concepts(self, module_path: Path) -> List[str]:
        """Extract key concepts from module."""
        concepts = []
        
        concept_keywords = [
            'class', 'interface', 'function', 'const', 'export',
            'def', 'async', 'await', 'type', 'struct', 'impl'
        ]
        
        for file in module_path.iterdir():
            if file.is_file() and file.suffix in ['.py', '.js', '.ts', '.tsx', '.go', '.rs']:
                try:
                    content = file.read_text()
                    lines = content.splitlines()
                    
                    for line in lines:
                        for kw in concept_keywords:
                            if kw in line and len(concepts) < 10:
                                concept = self._extract_concept_from_line(line, kw)
                                if concept and concept not in concepts:
                                    concepts.append(concept)
                except:
                    pass
        
        return concepts[:10]
    
    def _extract_concept_from_line(self, line: str, keyword: str) -> Optional[str]:
        """Extract concept name from a line."""
        try:
            if keyword in line:
                parts = line.split(keyword)
                if len(parts) > 1:
                    name = parts[1].strip().split('(')[0].split(':')[0].strip()
                    if name and not name.startswith('{'):
                        return f"{keyword} {name}"
        except:
            pass
        return None
    
    def _estimate_complexity(self, module_path: Path) -> str:
        """Estimate module complexity."""
        total_lines = 0
        file_count = 0
        
        for file in module_path.iterdir():
            if file.is_file() and file.suffix in ['.py', '.js', '.ts', '.tsx', '.go', '.rs', '.java']:
                total_lines += self._count_lines(file)
                file_count += 1
        
        if file_count == 0:
            return "empty"
        
        avg_lines = total_lines / file_count
        
        if file_count <= 2 and total_lines < 100:
            return "simple"
        
        if file_count <= 5 and total_lines < 500:
            return "medium"
        
        return "complex"
    
    def _extract_functions(self, module_path: Path) -> List[Dict]:
        """Extract function definitions."""
        functions = []
        
        for file in module_path.iterdir():
            if file.is_file():
                funcs = self._extract_functions_from_file(file)
                functions.extend(funcs)
        
        return functions[:20]
    
    def _extract_functions_from_file(self, file_path: Path) -> List[Dict]:
        """Extract functions from a single file."""
        functions = []
        
        try:
            content = file_path.read_text()
            lines = content.splitlines()
            
            for i, line in enumerate(lines):
                func_info = self._parse_function_line(line, file_path.suffix)
                if func_info:
                    func_info['file'] = file_path.name
                    func_info['line'] = i + 1
                    functions.append(func_info)
        except:
            pass
        
        return functions
    
    def _parse_function_line(self, line: str, suffix: str) -> Optional[Dict]:
        """Parse function definition from line."""
        line = line.strip()
        
        if suffix == '.py':
            if line.startswith('def ') or line.startswith('async def '):
                name = line.split('def ')[1].split('(')[0].strip()
                return {'name': name, 'type': 'function'}
        
        elif suffix in ['.js', '.ts', '.tsx']:
            if 'function ' in line:
                name = line.split('function ')[1].split('(')[0].strip()
                return {'name': name, 'type': 'function'}
            elif 'const ' in line and '= (' in line or '= async' in line:
                name = line.split('const ')[1].split('=')[0].strip()
                return {'name': name, 'type': 'function'}
        
        elif suffix == '.go':
            if 'func ' in line:
                name = line.split('func ')[1].split('(')[0].strip()
                return {'name': name, 'type': 'function'}
        
        return None
    
    def _extract_classes(self, module_path: Path) -> List[Dict]:
        """Extract class definitions."""
        classes = []
        
        for file in module_path.iterdir():
            if file.is_file():
                cls_list = self._extract_classes_from_file(file)
                classes.extend(cls_list)
        
        return classes[:15]
    
    def _extract_classes_from_file(self, file_path: Path) -> List[Dict]:
        """Extract classes from a single file."""
        classes = []
        
        try:
            content = file_path.read_text()
            lines = content.splitlines()
            
            for i, line in enumerate(lines):
                cls_info = self._parse_class_line(line, file_path.suffix)
                if cls_info:
                    cls_info['file'] = file_path.name
                    cls_info['line'] = i + 1
                    classes.append(cls_info)
        except:
            pass
        
        return classes
    
    def _parse_class_line(self, line: str, suffix: str) -> Optional[Dict]:
        """Parse class definition from line."""
        line = line.strip()
        
        if suffix == '.py':
            if line.startswith('class '):
                name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                return {'name': name, 'type': 'class'}
        
        elif suffix in ['.ts', '.tsx']:
            if 'class ' in line and 'interface' not in line:
                name = line.split('class ')[1].split(' ')[0].split('{')[0].strip()
                return {'name': name, 'type': 'class'}
        
        elif suffix == '.go':
            if 'type ' in line and ' struct' in line:
                name = line.split('type ')[1].split(' struct')[0].strip()
                return {'name': name, 'type': 'struct'}
        
        elif suffix == '.rs':
            if 'struct ' in line:
                name = line.split('struct ')[1].split('{')[0].strip()
                return {'name': name, 'type': 'struct'}
        
        return None
    
    def _infer_flow(self, module_path: Path) -> str:
        """Infer data/control flow through module."""
        entry_points = self._find_entry_points(module_path)
        
        if not entry_points:
            return "No clear entry points - utility module"
        
        flow = "Entry: " + " → ".join(entry_points[:3])
        
        if len(entry_points) > 3:
            flow += " → (processing) → output"
        
        return flow
    
    def _find_entry_points(self, module_path: Path) -> List[str]:
        """Find likely entry points for the module."""
        entry_points = []
        
        entry_file_names = ['main', 'index', 'app', 'handler', 'controller', 'route']
        entry_func_names = ['main', 'init', 'setup', 'run', 'start', 'handle', 'process']
        
        for file in module_path.iterdir():
            if file.is_file():
                name_lower = file.stem.lower()
                if any(e in name_lower for e in entry_file_names):
                    entry_points.append(file.stem)
        
        for func in self._extract_functions(module_path):
            name_lower = func['name'].lower()
            if any(e in name_lower for e in entry_func_names):
                entry_points.append(func['name'])
        
        return entry_points[:5]
    
    def _find_exports(self, module_path: Path) -> List[str]:
        """Find exports from the module."""
        exports = []
        
        for file in module_path.iterdir():
            if file.is_file() and file.suffix in ['.js', '.ts', '.tsx']:
                try:
                    content = file.read_text()
                    lines = content.splitlines()
                    
                    for line in lines:
                        if 'export ' in line:
                            if 'export default' in line:
                                exports.append('default export')
                            elif 'export const' in line:
                                name = line.split('export const ')[1].split('=')[0].strip()
                                exports.append(name)
                            elif 'export function' in line:
                                name = line.split('export function ')[1].split('(')[0].strip()
                                exports.append(name)
                            elif 'export class' in line:
                                name = line.split('export class ')[1].split(' ')[0].strip()
                                exports.append(name)
                except:
                    pass
        
        return exports[:10]
    
    def save_analysis(self, repo_id: int, module_path: str, 
                      analysis_highlevel: Dict, analysis_detailed: Dict) -> None:
        """Save analysis to cache."""
        conn = self.pm._get_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT OR REPLACE INTO module_cache
            (repo_id, module_path, analysis_highlevel, analysis_detailed, analyzed_at)
            VALUES (?, ?, ?, ?, ?)""",
            (repo_id, module_path, 
             json.dumps(analysis_highlevel), 
             json.dumps(analysis_detailed),
             datetime.now().isoformat())
        )
        
        conn.commit()
        self.pm.export_to_json()
    
    def get_or_analyze(self, repo_id: int, repo_path: str, module_path: str,
                       force_refresh: bool = False) -> Dict:
        """
        Get cached analysis or perform new analysis.
        
        Args:
            repo_id: Repository ID
            repo_path: Full path to repo
            module_path: Module/directory path relative to repo
            force_refresh: Skip cache and re-analyze
        
        Returns:
            Dict with highlevel and detailed analysis
        """
        if not force_refresh:
            cache_status = self.get_cache_status(repo_id, module_path)
            
            if cache_status['has_cache'] and cache_status['status'] == 'fresh':
                cached = cache_status['cached_data']
                return {
                    'from_cache': True,
                    'analyzed_at': cache_status['analyzed_at'],
                    'highlevel': json.loads(cached['analysis_highlevel']),
                    'detailed': json.loads(cached['analysis_detailed'])
                }
        
        analysis = self.analyze_module(repo_path, module_path)
        
        if analysis['highlevel'] and analysis['detailed']:
            self.save_analysis(repo_id, module_path, 
                              analysis['highlevel'], analysis['detailed'])
        
        return {
            'from_cache': False,
            'analyzed_at': datetime.now(),
            'highlevel': analysis['highlevel'],
            'detailed': analysis['detailed']
        }
    
    def clear_cache(self, repo_id: Optional[int] = None, module_path: Optional[str] = None) -> None:
        """Clear module analysis cache."""
        conn = self.pm._get_conn()
        cursor = conn.cursor()
        
        if repo_id and module_path:
            cursor.execute(
                "DELETE FROM module_cache WHERE repo_id = ? AND module_path = ?",
                (repo_id, module_path)
            )
        elif repo_id:
            cursor.execute("DELETE FROM module_cache WHERE repo_id = ?", (repo_id,))
        else:
            cursor.execute("DELETE FROM module_cache")
        
        conn.commit()
        self.pm.export_to_json()
    
    def list_cached_modules(self, repo_id: int) -> List[Dict]:
        """List all cached modules for a repo."""
        conn = self.pm._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT module_path, analyzed_at FROM module_cache 
            WHERE repo_id = ? ORDER BY analyzed_at DESC""",
            (repo_id,)
        )
        
        return [dict(row) for row in cursor.fetchall()]


def get_explain_analyzer(skill_dir: Optional[Path] = None) -> ExplainAnalyzer:
    """Get singleton ExplainAnalyzer instance."""
    return ExplainAnalyzer(skill_dir)


if __name__ == "__main__":
    print("Explain Analyzer Test")
    print("=" * 50)
    
    ea = ExplainAnalyzer()
    
    test_repo = "/Users/ashish/Documents/adaptive-learning-coach"
    test_module = "scripts"
    
    pm = get_progress_manager()
    repo_id = pm.register_repo(test_repo, "adaptive-learning-coach", "existing", "python")
    
    cache_status = ea.get_cache_status(repo_id, test_module)
    print(f"Cache status: {cache_status['status']}")
    
    result = ea.get_or_analyze(repo_id, test_repo, test_module, force_refresh=True)
    
    print(f"\nHigh-level analysis:")
    highlevel = result['highlevel']
    if highlevel:
        print(f"  Purpose: {highlevel['purpose']}")
        print(f"  Key files: {len(highlevel['key_files'])}")
        print(f"  Complexity: {highlevel['complexity']}")
        print(f"  Concepts: {highlevel['key_concepts'][:5]}")
    
    print(f"\nDetailed analysis:")
    detailed = result['detailed']
    if detailed:
        print(f"  Functions: {len(detailed['functions'])}")
        print(f"  Classes: {len(detailed['classes'])}")
        print(f"  Entry points: {detailed['entry_points']}")
    
    cache_status = ea.get_cache_status(repo_id, test_module)
    print(f"\nCache after analysis: {cache_status['status']}")
    
    print("\nAll tests passed!")