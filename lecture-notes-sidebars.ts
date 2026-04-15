import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';
import fs from 'fs';
import path from 'path';

type CourseConfigLite = {lectures?: {lectureId: string}[]};

function getLectureNotesSidebarItems(): string[] {
  const courseConfigPath = path.resolve(__dirname, 'course.config.json');

  try {
    const configRaw = fs.readFileSync(courseConfigPath, 'utf-8');
    const courseConfig = JSON.parse(configRaw) as CourseConfigLite;
    const lectureIds = (courseConfig.lectures || [])
      .map((lecture) => lecture.lectureId)
      .filter(Boolean);

    return ['index', ...lectureIds];
  } catch (error) {
    console.warn('Failed to load course.config.json for lecture notes sidebar. Falling back to index only.');
    return ['index'];
  }
}

const sidebars: SidebarsConfig = {
  lectureNotesSidebar: getLectureNotesSidebarItems(),
};

export default sidebars;