import {describe, expect, it} from '@jest/globals'

import {DependencyGraphConfig} from "../../src/configuration" 
import {toSnapshotRequest, retryTransientSubmission} from "../../src/dependency-graph"

describe('dependency-graph', () => {
    describe('constructs job correlator', () => {
        it('removes commas from workflow name', () => {
            const id = DependencyGraphConfig.constructJobCorrelator('Workflow, with,commas', 'jobid', '{}')
            expect(id).toBe('workflow_withcommas-jobid')
        })
        it('removes non word characters', () => {
            const id = DependencyGraphConfig.constructJobCorrelator('Workflow!_with()characters', 'job-*id', '{"foo": "bar!@#$%^&*("}')
            expect(id).toBe('workflow_withcharacters-job-id-bar')
        })
        it('replaces spaces', () => {
            const id = DependencyGraphConfig.constructJobCorrelator('Workflow !_ with () characters, and   spaces', 'job-*id', '{"foo": "bar!@#$%^&*("}')
            expect(id).toBe('workflow___with_characters_and_spaces-job-id-bar')
        })
        it('without matrix', () => {
            const id = DependencyGraphConfig.constructJobCorrelator('workflow', 'jobid', 'null')
            expect(id).toBe('workflow-jobid')
        })
        it('with dashes in values', () => {
            const id = DependencyGraphConfig.constructJobCorrelator('workflow-name', 'job-id', '{"os": "ubuntu-latest"}')
            expect(id).toBe('workflow-name-job-id-ubuntu-latest')
        })
        it('with single matrix value', () => {
            const id = DependencyGraphConfig.constructJobCorrelator('workflow', 'jobid', '{"os": "windows"}')
            expect(id).toBe('workflow-jobid-windows')
        })
        it('with composite matrix value', () => {
            const id = DependencyGraphConfig.constructJobCorrelator('workflow', 'jobid', '{"os": "windows", "java-version": "21.1", "other": "Value, with COMMA"}')
            expect(id).toBe('workflow-jobid-windows-211-value_with_comma')
        })
    })
    describe('constructs snapshot request', () => {
        it('copies snapshot fields and sets owner and repo', () => {
            const snapshot = {version: 0, job: {correlator: 'c', id: '1'}, sha: 'abc', ref: 'refs/heads/main', detector: {name: 'd'}, scanned: '2026-10-27T00:00:00Z', manifests: {}}
            expect(toSnapshotRequest(snapshot, 'owner', 'repo')).toEqual({owner: 'owner', repo: 'repo', ...snapshot})
        })
        it('drops request options supplied by the file', () => {
            const request = toSnapshotRequest({version: 0, url: 'https://attacker.example', baseUrl: 'https://attacker.example', headers: {}, method: 'GET', request: {}, owner: 'other', repo: 'other'}, 'owner', 'repo')
            expect(request).toEqual({owner: 'owner', repo: 'repo', version: 0})
        })
    })
})

describe('dependency snapshot transient HTTP retry (issue #656)', () => {
    it('retries HTTP 503 twice with bounded backoff and succeeds', async () => {
        let attempts = 0
        const delays: number[] = []
        const submit = async () => {
            attempts += 1
            if (attempts < 3) throw Object.assign(new Error('Service Unavailable'), {status: 503})
            return 'accepted'
        }
        const result = await retryTransientSubmission(submit, async ms => {
            delays.push(ms)
        })
        expect(result).toBe('accepted')
        expect(attempts).toBe(3)
        expect(delays).toEqual([1000, 2000])
    })

    it('preserves terminal failure after the two allowed retries', async () => {
        let attempts = 0
        const delays: number[] = []
        const failure = Object.assign(new Error('Bad Gateway'), {status: 502})
        const submit = async () => {
            attempts += 1
            throw failure
        }
        await expect(
            retryTransientSubmission(submit, async ms => {
                delays.push(ms)
            })
        ).rejects.toBe(failure)
        expect(attempts).toBe(3)
        expect(delays).toEqual([1000, 2000])
    })

    it('does not retry non-transient HTTP 403 or 422', async () => {
        for (const status of [403, 422]) {
            let attempts = 0
            const failure = Object.assign(new Error('Not retryable'), {status})
            await expect(
                retryTransientSubmission(
                    async () => {
                        attempts += 1
                        throw failure
                    },
                    async () => {
                        throw new Error('Unexpected retry wait')
                    }
                )
            ).rejects.toBe(failure)
            expect(attempts).toBe(1)
        }
    })

    it('does not retry an error with no HTTP status', async () => {
        let attempts = 0
        const failure = new Error('Unknown network outcome')
        await expect(
            retryTransientSubmission(
                async () => {
                    attempts += 1
                    throw failure
                },
                async () => {
                    throw new Error('Unexpected retry wait')
                }
            )
        ).rejects.toBe(failure)
        expect(attempts).toBe(1)
    })

    it('immediately returns on success without delay', async () => {
        const result = await retryTransientSubmission(async () => 'accepted', async () => {
            throw new Error('Unexpected retry wait')
        })
        expect(result).toBe('accepted')
    })
})
