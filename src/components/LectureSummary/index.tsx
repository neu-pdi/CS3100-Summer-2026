import { usePluginData } from '@docusaurus/useGlobalData';
import { GlobalPluginData } from '@docusaurus/plugin-content-docs/client';
import Link from '@docusaurus/Link';
import Markdown from 'react-markdown';
import { Box, Card, HStack, List, Text, Heading } from '@chakra-ui/react';
import {decode} from 'html-entities';

type LectureHeading = {
    text: string;
    id: string;
};

type LectureSummaryData = {
    id: string;
    title: string;
    lectureNumber?: number;
    requiredPreparation: string[];
    optionalPreparation: string[];
    headings: LectureHeading[];
    estimatedMinutes: number;
};

type ClassasaurusData = {
    lectureSummaries?: LectureSummaryData[];
};

export default function LectureSummary({ version }: { version: string }) {
    const docsPluginData = usePluginData('docusaurus-plugin-content-docs') as GlobalPluginData;
    const classasaurusData = usePluginData('docusaurus-plugin-classasaurus') as ClassasaurusData;
    const docsById = new Map(
        docsPluginData.versions[0].docs
            .filter((doc) => !doc.id.startsWith('l0'))
            .map((doc) => [doc.id, doc])
    );
    const docs = (classasaurusData.lectureSummaries || [])
        .map((summary) => ({
            doc: docsById.get(summary.id),
            summary,
        }))
        .filter((entry) => entry.doc);

    docs.sort((a, b) => a.summary.id.localeCompare(b.summary.id, undefined, { numeric: true, sensitivity: 'accent' }));

    return (
        <Box>
            {docs.map(({ doc, summary }) => {
                if (!doc) {
                    return null;
                }

                return (
                    <Card.Root key={doc.id} m={4} size='sm'>
                        <Card.Header>
                            <HStack justifyContent='space-between'>
                                <Link to={doc.path}><Heading as="h3" m={0}>{summary.lectureNumber ? `${summary.lectureNumber}. ${summary.title}` : summary.title}</Heading></Link>
                                <Text fontSize='sm' color='text.muted'>Est {summary.estimatedMinutes} minutes</Text>
                            </HStack>
                        </Card.Header>
                        <Card.Body spaceY={0}>
                            <HStack alignItems="flex-start">
                                {summary.requiredPreparation.length > 0 && <Box>
                                    <Text fontWeight='bold' p={0} m={0}>Required preparation</Text>
                                    <List.Root m={0}>
                                        {summary.requiredPreparation.map((prep, idx) => <List.Item key={idx}><a href={prep}>{prep}</a></List.Item>)}
                                    </List.Root>
                                </Box>}
                                {summary.optionalPreparation.length > 0 && <Box>
                                    <Text fontWeight='bold' p={0} m={0}>Optional preparation</Text>
                                    <List.Root m={0}>
                                        {summary.optionalPreparation.map((prep, idx) => <List.Item key={idx}><Markdown>{prep}</Markdown></List.Item>)}
                                    </List.Root>
                                </Box>}
                            </HStack>
                            <b>Topics</b>
                            <List.Root>
                                {summary.headings.map((heading, idx) => (
                                    <List.Item key={idx}>
                                        <Link to={`${doc.path}#${heading.id}`}>{decode(heading.text)}</Link>
                                    </List.Item>
                                ))}
                            </List.Root>
                        </Card.Body>
                    </Card.Root>
                );
            })}
        </Box>
    )
}