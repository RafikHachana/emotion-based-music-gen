import Head from "next/head";
import { Inter } from "next/font/google";
import { Box, Flex, Image, Text } from "@chakra-ui/react";


const inter = Inter({ subsets: ["latin"] });

export default function Home() {
    return (
        <>
            <Head>
                <title>Emotions to Music Generator</title>
                <meta 
                    name="description" 
                    content="Emotions to Music Generator (Innopolis University Advanced Machine Learning)" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <link rel="icon" href="/favicon.ico" />
            </Head>
            
            <Box as="main" role="main" bg="bg.default" p="4">
                <Text fontSize="2xl" fontWeight="bold" textAlign="center">
                    Emotions to Music Generator
                </Text>
                <Text fontSize={'xl'} mt={10} textAlign={'center'}>
                    To generate music from emotions, please go to the tab Generate!.
                </Text>
                <Flex justifyContent="center" alignItems="center" flexDir={'column'}>
                    <Text>
                        The model training is described in the following images.
                    </Text>
                    <Box mt={10} width={600} height={500} background={"white"}>
                        <Image src="/model-training.png" alt="model-training" />
                    </Box>
                    <Text mt={10}>
                        The inference is described in the following image.
                    </Text>
                    <Box mt={10} width={700} height={300}>
                        <Image src="/inference.jpg" alt="inference" />
                    </Box>
                </Flex>
            </Box>
        </>
    );
}
