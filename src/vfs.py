"""Виртуальная файловая система (VFS).

Этап 3. Загрузка VFS из XML-файла в память.
Этап 4. Разрешение относительных путей.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class VfsError(Exception):
    """Ошибка работы с VFS."""


@dataclass
class VfsNode:
    """Узел виртуальной файловой системы.

    Может быть как директорией, так и файлом.

    Attributes:
        name: Имя узла.
        is_dir: True, если это директория.
        content: Содержимое файла (None для директорий).
        children: Дочерние узлы (для директорий).
    """

    name: str
    is_dir: bool
    content: Optional[str] = None
    children: Dict[str, "VfsNode"] = field(default_factory=dict)

    def list_children(self) -> List[str]:
        """Вернуть имена дочерних узлов, отсортированные."""
        return sorted(self.children.keys())

    def get_child(self, name: str) -> Optional["VfsNode"]:
        """Вернуть дочерний узел по имени или None."""
        return self.children.get(name)


@dataclass
class VirtualFileSystem:
    """Виртуальная файловая система в памяти."""

    name: str
    root: VfsNode

    @property
    def motd(self) -> Optional[str]:
        """Содержимое файла motd из корня или None."""
        node = self.root.get_child("motd")
        if node is None or node.is_dir:
            return None
        return node.content

    def resolve(self, path: str) -> Optional[VfsNode]:
        """Найти узел по абсолютному пути.

        Args:
            path: Абсолютный путь, начинающийся с '/'.

        Returns:
            Узел или None, если путь не существует.
        """
        if not path.startswith("/"):
            return None
        parts = [p for p in path.split("/") if p]
        node = self.root
        for part in parts:
            if not node.is_dir:
                return None
            child = node.get_child(part)
            if child is None:
                return None
            node = child
        return node

    """Найти узел по пути относительно cwd.

            Поддерживает абсолютные и относительные пути,
            а также элементы '.' и '..'.

            Args:
                cwd: Текущая директория (абсолютный путь).
                path: Путь (абсолютный или относительный).

            Returns:
                Узел или None, если путь не существует.
            """

    def resolve_path(
        self,
        cwd: str,
        path: str,
    ) -> Optional[VfsNode]:

        if not path:
            return self.resolve(cwd)

        if path.startswith("/"):
            parts = [p for p in path.split("/") if p]
        else:
            base = [p for p in cwd.split("/") if p]
            parts = base + [p for p in path.split("/") if p]

        normalized: List[str] = []
        for part in parts:
            if part == ".":
                continue
            if part == "..":
                if normalized:
                    normalized.pop()
                continue
            normalized.append(part)

        node = self.root
        for part in normalized:
            if not node.is_dir:
                return None
            child = node.get_child(part)
            if child is None:
                return None
            node = child
        return node


def load_vfs(path: str) -> VirtualFileSystem:
    """Загрузить VFS из XML-файла.

    Args:
        path: Путь к XML-файлу.

    Returns:
        Объект VirtualFileSystem.

    Raises:
        VfsError: Если файл не найден, не является корректным
            XML или имеет неверную структуру.
    """
    try:
        tree = ET.parse(path)
    except FileNotFoundError as exc:
        raise VfsError(f"VFS file not found: {path}") from exc
    except ET.ParseError as exc:
        raise VfsError(f"VFS parse error: {exc}") from exc

    root_elem = tree.getroot()
    if root_elem.tag != "vfs":
        raise VfsError(
            f"Invalid VFS: root tag must be 'vfs', "
            f"got '{root_elem.tag}'"
        )

    name = root_elem.get("name", "unnamed")
    root_node = VfsNode(name="/", is_dir=True)

    for child_elem in root_elem:
        node = _parse_node(child_elem)
        if node.name in root_node.children:
            raise VfsError(
                f"Duplicate entry in root: '{node.name}'"
            )
        root_node.children[node.name] = node

    return VirtualFileSystem(name=name, root=root_node)


def _parse_node(elem: ET.Element) -> VfsNode:
    """Разобрать один XML-элемент в узел VFS.

    Args:
        elem: XML-элемент.

    Returns:
        Узел VfsNode.

    Raises:
        VfsError: Если тег неизвестен или нет атрибута name.
    """
    name = elem.get("name")
    if not name:
        raise VfsError(
            f"Missing 'name' attribute in <{elem.tag}>"
        )

    if elem.tag == "dir":
        return _parse_dir(elem, name)

    if elem.tag == "file":
        return _parse_file(elem, name)

    raise VfsError(f"Unknown tag: <{elem.tag}>")


def _parse_dir(elem: ET.Element, name: str) -> VfsNode:
    """Создать узел-директорию из XML-элемента.

    Args:
        elem: XML-элемент <dir>.
        name: Имя директории.

    Returns:
        Узел VfsNode.

    Raises:
        VfsError: Если найдены дублирующиеся имена.
    """
    node = VfsNode(name=name, is_dir=True)
    for child_elem in elem:
        child = _parse_node(child_elem)
        if child.name in node.children:
            raise VfsError(
                f"Duplicate entry in '{name}': '{child.name}'"
            )
        node.children[child.name] = child
    return node


def _parse_file(elem: ET.Element, name: str) -> VfsNode:
    """Создать узел-файл из XML-элемента.

    Args:
        elem: XML-элемент <file>.
        name: Имя файла.

    Returns:
        Узел VfsNode.
    """
    content = elem.text if elem.text is not None else ""
    return VfsNode(name=name, is_dir=False, content=content)


def empty_vfs(name: str = "my_vfs") -> VirtualFileSystem:
    """Создать пустую VFS в памяти.

    Args:
        name: Имя VFS.

    Returns:
        Пустая VFS с одним корневым узлом.
    """
    root = VfsNode(name="/", is_dir=True)
    return VirtualFileSystem(name=name, root=root)