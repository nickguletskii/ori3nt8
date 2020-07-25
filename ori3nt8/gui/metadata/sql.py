#  Copyright 2020 Nick Guletskii
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import sqlite3
from pathlib import Path
from typing import Optional

import appdirs
from sqlalchemy import Column, Integer, Text, SmallInteger, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ori3nt8.gui.metadata.common import Metadata, AbstractMetadataStorage

Base = declarative_base()


class MetadataTable(Base):
    __tablename__ = "metadata"
    id = Column(Integer, primary_key=True)
    path = Column(Text, unique=True)
    original_orientation = Column(SmallInteger)
    suggested_orientation = Column(SmallInteger, nullable=True)
    orientation_was_selected_manually = Column(Boolean)
    orientation_was_selected_automatically = Column(Boolean)


class SqliteMetadataStorage(AbstractMetadataStorage):
    def __init__(self):
        database_path = Path(appdirs.user_data_dir("ori3nt8")) / "metadata.db"
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(database_path))
        engine = create_engine(f"sqlite:///{str(database_path)}", echo=False)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def dump(self, path: Path, metadata: Metadata):
        entity = self.session.query(MetadataTable).filter_by(path=str(path)).first()
        if not entity:
            entity = MetadataTable(
                path=str(path),
                original_orientation=metadata.original_orientation,
                suggested_orientation=metadata.suggested_orientation,
                orientation_was_selected_manually=metadata.orientation_was_selected_manually,
                orientation_was_selected_automatically=metadata.orientation_was_selected_automatically,
            )
            self.session.add(entity)
        else:
            entity.original_orientation = metadata.original_orientation
            entity.suggested_orientation = metadata.suggested_orientation
            entity.orientation_was_selected_manually = metadata.orientation_was_selected_manually
            entity.orientation_was_selected_automatically = metadata.orientation_was_selected_automatically
        self.session.commit()
        return entity

    def load(self, path: Path) -> Optional[Metadata]:
        entity = self.session.query(MetadataTable).filter_by(path=str(path)).first()
        if not entity:
            return None

        return Metadata(
            original_orientation=entity.original_orientation,
            suggested_orientation=entity.suggested_orientation,
            orientation_was_selected_manually=entity.orientation_was_selected_manually,
            orientation_was_selected_automatically=entity.orientation_was_selected_automatically,
        )
