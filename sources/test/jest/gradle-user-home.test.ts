import * as path from 'path'
import * as fs from 'fs'
import {describe, expect, it} from '@jest/globals'

import {configureInfoLogLevel, restoreInfoLogLevel} from '../../src/gradle-user-home'

const testTmp = 'test/jest/tmp'
fs.rmSync(testTmp, {recursive: true, force: true})

describe("--info and --stacktrace", () => {
    describe("will be created", () => {
        it("when gradle.properties does not exist", async () => {
            const emptyGradleHome = `${testTmp}/empty-gradle-home`
            fs.mkdirSync(emptyGradleHome, {recursive: true})

            configureInfoLogLevel(emptyGradleHome)

            expect(fs.readFileSync(path.resolve(emptyGradleHome, "gradle.properties"), 'utf-8'))
                .toBe("org.gradle.logging.level=info\norg.gradle.logging.stacktrace=all\n")
        })
    })
    describe("will be added", () => {
        it("and gradle.properties does exists", async () => {
            const existingGradleHome = `${testTmp}/existing-gradle-home`
            fs.mkdirSync(existingGradleHome, {recursive: true})
            fs.writeFileSync(path.resolve(existingGradleHome, "gradle.properties"), "org.gradle.logging.level=debug\n")

            configureInfoLogLevel(existingGradleHome)

            expect(fs.readFileSync(path.resolve(existingGradleHome, "gradle.properties"), 'utf-8'))
                .toBe("org.gradle.logging.level=info\norg.gradle.logging.stacktrace=all\n\norg.gradle.logging.level=debug\n")
        })
    })
})

describe('post-action debug properties cleanup (issue #549)', () => {
    const stateKey = 'STATE_GRADLE_DEBUG_PROPERTIES'

    function restoreAfterSetup(gradleHome: string, existedBefore: boolean): void {
        process.env[stateKey] = JSON.stringify({
            propertiesFile: path.resolve(gradleHome, 'gradle.properties'),
            existedBefore
        })
        try {
            restoreInfoLogLevel()
        } finally {
            delete process.env[stateKey]
        }
    }

    it('removes only the properties file created in debug mode', () => {
        const gradleHome = `${testTmp}/post-created`
        fs.mkdirSync(gradleHome, {recursive: true})
        configureInfoLogLevel(gradleHome)
        restoreAfterSetup(gradleHome, false)
        expect(fs.existsSync(path.resolve(gradleHome, 'gradle.properties'))).toBe(false)
    })

    it('restores the exact original bytes of an existing properties file', () => {
        const gradleHome = `${testTmp}/post-existing`
        fs.mkdirSync(gradleHome, {recursive: true})
        const file = path.resolve(gradleHome, 'gradle.properties')
        const original = 'org.gradle.logging.level=debug\ncustom.setting=yes\n'
        fs.writeFileSync(file, original)
        configureInfoLogLevel(gradleHome)
        restoreAfterSetup(gradleHome, true)
        expect(fs.readFileSync(file, 'utf8')).toBe(original)
    })

    it('preserves properties appended by the build after debug setup', () => {
        const gradleHome = `${testTmp}/post-modified`
        fs.mkdirSync(gradleHome, {recursive: true})
        const file = path.resolve(gradleHome, 'gradle.properties')
        fs.writeFileSync(file, 'original=true\n')
        configureInfoLogLevel(gradleHome)
        fs.appendFileSync(file, 'build-added=true\n')
        restoreAfterSetup(gradleHome, true)
        expect(fs.readFileSync(file, 'utf8')).toBe('original=true\nbuild-added=true\n')
    })

    it('keeps properties written after creating a temporary debug file', () => {
        const gradleHome = `${testTmp}/post-created-extended`
        fs.mkdirSync(gradleHome, {recursive: true})
        const file = path.resolve(gradleHome, 'gradle.properties')
        configureInfoLogLevel(gradleHome)
        fs.appendFileSync(file, 'added-after-setup=true\n')
        restoreAfterSetup(gradleHome, false)
        expect(fs.readFileSync(file, 'utf8')).toBe('added-after-setup=true\n')
    })

    it('does not recreate a temporary file already removed during the job', () => {
        const gradleHome = `${testTmp}/post-removed`
        fs.mkdirSync(gradleHome, {recursive: true})
        const file = path.resolve(gradleHome, 'gradle.properties')
        configureInfoLogLevel(gradleHome)
        fs.unlinkSync(file)
        restoreAfterSetup(gradleHome, false)
        expect(fs.existsSync(file)).toBe(false)
    })

    it('preserves an independently rewritten file when the injected prefix is absent', () => {
        const gradleHome = `${testTmp}/post-rewritten`
        fs.mkdirSync(gradleHome, {recursive: true})
        const file = path.resolve(gradleHome, 'gradle.properties')
        configureInfoLogLevel(gradleHome)
        fs.writeFileSync(file, 'replaced-by-user=true\n')
        restoreAfterSetup(gradleHome, false)
        expect(fs.readFileSync(file, 'utf8')).toBe('replaced-by-user=true\n')
    })

    it('does nothing when the debug step did not save a valid state', () => {
        const gradleHome = `${testTmp}/post-invalid-state`
        fs.mkdirSync(gradleHome, {recursive: true})
        const file = path.resolve(gradleHome, 'gradle.properties')
        fs.writeFileSync(file, 'keep=true\n')
        process.env[stateKey] = '{not-json'
        try {
            restoreInfoLogLevel()
        } finally {
            delete process.env[stateKey]
        }
        expect(fs.readFileSync(file, 'utf8')).toBe('keep=true\n')
    })

    it('does not follow a replacement symlink on the cleanup path', () => {
        if (process.platform === 'win32') return
        const gradleHome = `${testTmp}/post-symlink`
        fs.mkdirSync(gradleHome, {recursive: true})
        const file = path.resolve(gradleHome, 'gradle.properties')
        const other = path.resolve(gradleHome, 'other.properties')
        configureInfoLogLevel(gradleHome)
        fs.renameSync(file, other)
        fs.symlinkSync(other, file)
        restoreAfterSetup(gradleHome, false)
        expect(fs.lstatSync(file).isSymbolicLink()).toBe(true)
        expect(fs.readFileSync(other, 'utf8')).toContain('org.gradle.logging.level=info')
    })
})
