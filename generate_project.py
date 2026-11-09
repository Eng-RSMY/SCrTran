#!/usr/bin/env python3
"""
Generates a correct Xcode project (.xcodeproj) for ScreenTranslator:
  - ScreenTranslator            (iOS App, SwiftUI)
  - ScreenTranslatorBroadcast   (Broadcast Upload Extension)

Run on macOS:  python3 generate_project.py
Then open ScreenTranslator.xcodeproj in Xcode, set your bundle ids / signing /
App Group, and archive to produce an .ipa.

The project uses objectVersion 56 (Xcode 14+). All UUIDs are derived from
deterministic seeds so re-running is stable.
"""

import hashlib
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_NAME = "ScreenTranslator"
APP_TARGET = "ScreenTranslator"
EXT_TARGET = "ScreenTranslatorBroadcast"
APP_BUNDLE = "com.example.screentranslator"
EXT_BUNDLE = "com.example.screentranslator.broadcast"
APP_GROUP = "group.com.example.screentranslator"
DEPLOYMENT_TARGET = "16.0"


def uid(seed: str) -> str:
    return hashlib.sha256(("ST:" + seed).encode()).digest()[:12].hex()


# ---------------------------------------------------------------------------
# Stable identifiers
# ---------------------------------------------------------------------------
proj_uid = uid("PBXProject")
app_target_uid = uid("app_target")
ext_target_uid = uid("ext_target")
app_product_uid = uid("app_product")
ext_product_uid = uid("ext_product")
app_list_uid = uid("app_configlist")
ext_list_uid = uid("ext_configlist")
proj_list_uid = uid("proj_configlist")
app_src_phase = uid("app_src")
app_fw_phase = uid("app_fw")
app_res_phase = uid("app_res")
app_embed_phase = uid("app_embed")
ext_src_phase = uid("ext_src")
ext_fw_phase = uid("ext_fw")
ext_res_phase = uid("ext_res")
dependency_uid = uid("app_dep")
proxy_uid = uid("container_proxy")
root_group = uid("root_group")
app_group_g = uid("g_app")
shared_group_g = uid("g_shared")
ext_group_g = uid("g_ext")
fw_group_g = uid("g_fw")
products_group_g = uid("g_products")

proj_debug = uid("proj_debug")
proj_release = uid("proj_release")
app_debug = uid("app_debug")
app_release = uid("app_release")
ext_debug = uid("ext_debug")
ext_release = uid("ext_release")

# ---------------------------------------------------------------------------
# File lists (relative paths from project root)
# ---------------------------------------------------------------------------
app_sources = [
    "ScreenTranslator/ScreenTranslatorApp.swift",
    "ScreenTranslator/TranslationStore.swift",
    "ScreenTranslator/ContentView.swift",
    "ScreenTranslator/SettingsView.swift",
    "ScreenTranslator/LiveOverlayView.swift",
]
shared_sources = [
    "Shared/AppGroup.swift",
    "Shared/TranslationModels.swift",
    "Shared/TranslationService.swift",
    "Shared/OCRManager.swift",
]
ext_sources = [
    "ScreenTranslatorBroadcast/SampleHandler.swift",
]

app_resource_files = [
    "ScreenTranslator/Info.plist",
    "ScreenTranslator/ScreenTranslator.entitlements",
]
ext_resource_files = [
    "ScreenTranslatorBroadcast/Info.plist",
    "ScreenTranslatorBroadcast/ScreenTranslatorBroadcast.entitlements",
]

# Shared sources are compiled into BOTH targets.
app_compile = app_sources + shared_sources
ext_compile = ext_sources + shared_sources

# System frameworks
app_frameworks = ["Vision", "ReplayKit", "PhotosUI"]
ext_frameworks = ["Vision", "ReplayKit"]


def file_uid(path: str) -> str:
    return uid("file:" + path)


def buildfile_uid(target: str, path: str) -> str:
    return uid("bf:" + target + ":" + path)


def fw_file_uid(name: str) -> str:
    return uid("fw:" + name)


def fw_buildfile_uid(target: str, name: str) -> str:
    return uid("bfw:" + target + ":" + name)


def base_name(path: str) -> str:
    return os.path.basename(path)


# ---------------------------------------------------------------------------
# Build the project.pbxproj
# ---------------------------------------------------------------------------
L = []


def w(line: str = ""):
    L.append(line)


def comment(title: str):
    w("\t\t/* Begin " + title + " */")


def endcomment(title: str):
    w("\t\t/* End " + title + " */")


# --- PBXBuildFile ---
comment("PBXBuildFile section")
for path in app_compile:
    w('\t\t%s /* %s in Sources */ = {isa = PBXBuildFile; fileRef = %s /* %s */; };' % (
        buildfile_uid(APP_TARGET, path), base_name(path), file_uid(path), base_name(path)))
for path in ext_compile:
    w('\t\t%s /* %s in Sources */ = {isa = PBXBuildFile; fileRef = %s /* %s */; };' % (
        buildfile_uid(EXT_TARGET, path), base_name(path), file_uid(path), base_name(path)))
for name in app_frameworks:
    w('\t\t%s /* %s.framework in Frameworks */ = {isa = PBXBuildFile; fileRef = %s /* %s.framework */; };' % (
        fw_buildfile_uid(APP_TARGET, name), name, fw_file_uid(name), name))
for name in ext_frameworks:
    w('\t\t%s /* %s.framework in Frameworks */ = {isa = PBXBuildFile; fileRef = %s /* %s.framework */; };' % (
        fw_buildfile_uid(EXT_TARGET, name), name, fw_file_uid(name), name))
# Embed extension product
w('\t\t%s /* %s.appex in Embed App Extensions */ = {isa = PBXBuildFile; fileRef = %s /* %s.appex */; settings = {ATTRIBUTES = (RemoveHeadersOnCopy, ); }; };' % (
    uid("embed_bf"), EXT_TARGET, ext_product_uid, EXT_TARGET))
endcomment("PBXBuildFile section")
w()

# --- PBXContainerItemProxy ---
comment("PBXContainerItemProxy section")
w('\t\t%s /* PBXContainerItemProxy */ = {' % proxy_uid)
w("\t\t\tisa = PBXContainerItemProxy;")
w("\t\t\tcontainerPortal = %s /* Project object */;" % proj_uid)
w("\t\t\tproxyType = 1;")
w("\t\t\tremoteGlobalIDString = %s;" % ext_target_uid)
w("\t\t\tremoteInfo = %s;" % EXT_TARGET)
w("\t\t};")
endcomment("PBXContainerItemProxy section")
w()

# --- PBXFileReference ---
comment("PBXFileReference section")
for path in app_compile + shared_sources + ext_compile:
    w('\t\t%s /* %s */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = "%s"; sourceTree = "<group>"; };' % (
        file_uid(path), base_name(path), base_name(path)))
for path in app_resource_files + ext_resource_files:
    is_ent = path.endswith(".entitlements")
    lkft = "text.plist.entitlements" if is_ent else "text.plist.xml"
    w('\t\t%s /* %s */ = {isa = PBXFileReference; lastKnownFileType = %s; path = "%s"; sourceTree = "<group>"; };' % (
        file_uid(path), base_name(path), lkft, base_name(path)))
for name in set(app_frameworks + ext_frameworks):
    w('\t\t%s /* %s.framework */ = {isa = PBXFileReference; lastKnownFileType = wrapper.framework; name = "%s.framework"; path = "System/Library/Frameworks/%s.framework"; sourceTree = SDKROOT; };' % (
        fw_file_uid(name), name, name, name))
# Products
w('\t\t%s /* %s.app */ = {isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = "%s.app"; sourceTree = BUILT_PRODUCTS_DIR; };' % (
    app_product_uid, APP_TARGET, APP_TARGET))
w('\t\t%s /* %s.appex */ = {isa = PBXFileReference; explicitFileType = "wrapper.app-extension"; includeInIndex = 0; path = "%s.appex"; sourceTree = BUILT_PRODUCTS_DIR; };' % (
    ext_product_uid, EXT_TARGET, EXT_TARGET))
endcomment("PBXFileReference section")
w()

# --- PBXFrameworksBuildPhase ---
comment("PBXFrameworksBuildPhase section")


def frameworks_phase(uid_key, files):
    w("\t\t%s /* Frameworks */ = {" % uid_key)
    w("\t\t\tisa = PBXFrameworksBuildPhase;")
    w("\t\t\tbuildActionMask = 2147483647;")
    w("\t\t\tfiles = (")
    for f in files:
        w("\t\t\t\t%s," % f)
    w("\t\t\t);")
    w("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
    w("\t\t};")


app_fw_files = [fw_buildfile_uid(APP_TARGET, n) for n in app_frameworks]
ext_fw_files = [fw_buildfile_uid(EXT_TARGET, n) for n in ext_frameworks]
frameworks_phase(app_fw_phase, app_fw_files)
frameworks_phase(ext_fw_phase, ext_fw_files)
endcomment("PBXFrameworksBuildPhase section")
w()

# --- PBXGroup ---
comment("PBXGroup section")


def group(uid_key, children, path=None):
    w("\t\t%s = {" % uid_key)
    w("\t\t\tisa = PBXGroup;")
    w("\t\t\tchildren = (")
    for c in children:
        w("\t\t\t\t%s," % c)
    w("\t\t\t);")
    w("\t\t\tsourceTree = \"<group>\";")
    if path is not None:
        w("\t\t\tpath = \"%s\";" % path)
    w("\t\t};")


app_group_children = [file_uid(p) for p in app_compile] + [file_uid(p) for p in app_resource_files]
shared_group_children = [file_uid(p) for p in shared_sources]
ext_group_children = [file_uid(p) for p in ext_compile] + [file_uid(p) for p in ext_resource_files]
fw_group_children = [fw_file_uid(n) for n in set(app_frameworks + ext_frameworks)]
products_group_children = [app_product_uid, ext_product_uid]

root_children = [app_group_g, shared_group_g, ext_group_g, fw_group_g, products_group_g]

group(root_group, root_children)
group(app_group_g, app_group_children, "ScreenTranslator")
group(shared_group_g, shared_group_children, "Shared")
group(ext_group_g, ext_group_children, "ScreenTranslatorBroadcast")
group(fw_group_g, fw_group_children)
group(products_group_g, products_group_children)
endcomment("PBXGroup section")
w()

# --- PBXNativeTarget ---
comment("PBXNativeTarget section")
w("\t\t%s /* %s */ = {" % (app_target_uid, APP_TARGET))
w("\t\t\tisa = PBXNativeTarget;")
w("\t\t\tbuildConfigurationList = %s /* Build configuration list for %s */;" % (app_list_uid, APP_TARGET))
w("\t\t\tbuildPhases = (")
w("\t\t\t\t%s /* Sources */," % app_src_phase)
w("\t\t\t\t%s /* Frameworks */," % app_fw_phase)
w("\t\t\t\t%s /* Resources */," % app_res_phase)
w("\t\t\t\t%s /* Embed App Extensions */," % app_embed_phase)
w("\t\t\t);")
w("\t\t\tbuildRules = (")
w("\t\t\t);")
w("\t\t\tdependencies = (")
w("\t\t\t\t%s /* PBXTargetDependency */," % dependency_uid)
w("\t\t\t);")
w("\t\t\tname = %s;" % APP_TARGET)
w("\t\t\tproductName = %s;" % APP_TARGET)
w("\t\t\tproductReference = %s /* %s.app */;" % (app_product_uid, APP_TARGET))
w("\t\t\tproductType = \"com.apple.product-type.application\";")
w("\t\t};")
w()
w("\t\t%s /* %s */ = {" % (ext_target_uid, EXT_TARGET))
w("\t\t\tisa = PBXNativeTarget;")
w("\t\t\tbuildConfigurationList = %s /* Build configuration list for %s */;" % (ext_list_uid, EXT_TARGET))
w("\t\t\tbuildPhases = (")
w("\t\t\t\t%s /* Sources */," % ext_src_phase)
w("\t\t\t\t%s /* Frameworks */," % ext_fw_phase)
w("\t\t\t\t%s /* Resources */," % ext_res_phase)
w("\t\t\t);")
w("\t\t\tbuildRules = (")
w("\t\t\t);")
w("\t\t\tdependencies = (")
w("\t\t\t);")
w("\t\t\tname = %s;" % EXT_TARGET)
w("\t\t\tproductName = %s;" % EXT_TARGET)
w("\t\t\tproductReference = %s /* %s.appex */;" % (ext_product_uid, EXT_TARGET))
w("\t\t\tproductType = \"com.apple.product-type.app-extension\";")
w("\t\t};")
endcomment("PBXNativeTarget section")
w()

# --- PBXProject ---
comment("PBXProject section")
w("\t\t%s /* Project object */ = {" % proj_uid)
w("\t\t\tisa = PBXProject;")
w("\t\t\tattributes = {")
w("\t\t\t\tBuildIndependentTargetsInParallel = 1;")
w("\t\t\t\tLastUpgradeCheck = 1500;")
w("\t\t\t\tTargetAttributes = {")
w("\t\t\t\t\t%s = {CreatedOnToolsVersion = 15.0;};" % app_target_uid)
w("\t\t\t\t\t%s = {CreatedOnToolsVersion = 15.0;};" % ext_target_uid)
w("\t\t\t\t};")
w("\t\t\t};")
w("\t\t\tbuildConfigurationList = %s /* Build configuration list for PBXProject */;" % proj_list_uid)
w("\t\t\tcompatibilityVersion = \"Xcode 14.0\";")
w("\t\t\tdevelopmentRegion = en;")
w("\t\t\thasScannedForEncodings = 0;")
w("\t\t\tknownRegions = (")
w("\t\t\t\ten,")
w("\t\t\t\tBase,")
w("\t\t\t);")
w("\t\t\tmainGroup = %s;" % root_group)
w("\t\t\tproductRefGroup = %s /* Products */;" % products_group_g)
w("\t\t\tprojectDirPath = \"\";")
w("\t\t\tprojectRoot = \"\";")
w("\t\t\ttargets = (")
w("\t\t\t\t%s /* %s */," % (app_target_uid, APP_TARGET))
w("\t\t\t\t%s /* %s */," % (ext_target_uid, EXT_TARGET))
w("\t\t\t);")
w("\t\t};")
endcomment("PBXProject section")
w()

# --- PBXResourcesBuildPhase (empty, plists are referenced via INFOPLIST_FILE) ---
comment("PBXResourcesBuildPhase section")
for uid_key in (app_res_phase, ext_res_phase):
    w("\t\t%s /* Resources */ = {" % uid_key)
    w("\t\t\tisa = PBXResourcesBuildPhase;")
    w("\t\t\tbuildActionMask = 2147483647;")
    w("\t\t\tfiles = (")
    w("\t\t\t);")
    w("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
    w("\t\t};")
endcomment("PBXResourcesBuildPhase section")
w()

# --- PBXSourcesBuildPhase ---
comment("PBXSourcesBuildPhase section")
app_src_files = [buildfile_uid(APP_TARGET, p) for p in app_compile]
ext_src_files = [buildfile_uid(EXT_TARGET, p) for p in ext_compile]
for uid_key, files in ((app_src_phase, app_src_files), (ext_src_phase, ext_src_files)):
    w("\t\t%s /* Sources */ = {" % uid_key)
    w("\t\t\tisa = PBXSourcesBuildPhase;")
    w("\t\t\tbuildActionMask = 2147483647;")
    w("\t\t\tfiles = (")
    for f in files:
        w("\t\t\t\t%s," % f)
    w("\t\t\t);")
    w("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
    w("\t\t};")
endcomment("PBXSourcesBuildPhase section")
w()

# --- PBXTargetDependency ---
comment("PBXTargetDependency section")
w("\t\t%s /* PBXTargetDependency */ = {" % dependency_uid)
w("\t\t\tisa = PBXTargetDependency;")
w("\t\t\ttarget = %s /* %s */;" % (ext_target_uid, EXT_TARGET))
w("\t\t\ttargetProxy = %s /* PBXContainerItemProxy */;" % proxy_uid)
w("\t\t};")
endcomment("PBXTargetDependency section")
w()

# --- PBXCopyFilesBuildPhase (Embed App Extensions) ---
comment("PBXCopyFilesBuildPhase section")
w("\t\t%s /* Embed App Extensions */ = {" % app_embed_phase)
w("\t\t\tisa = PBXCopyFilesBuildPhase;")
w("\t\t\tbuildActionMask = 2147483647;")
w("\t\t\tdstPath = \"\";")
w("\t\t\tdstSubfolderSpec = 13;")
w("\t\t\tfiles = (")
w("\t\t\t\t%s /* %s.appex in Embed App Extensions */," % (uid("embed_bf"), EXT_TARGET))
w("\t\t\t);")
w("\t\t\tname = \"Embed App Extensions\";")
w("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
w("\t\t};")
endcomment("PBXCopyFilesBuildPhase section")
w()

# --- XCBuildConfiguration ---
comment("XCBuildConfiguration section")

PROJECT_DEBUG_SETTINGS = """\
\t\t\t\tCLANG_ANALYZER_NONNULL = YES;
\t\t\t\tCLANG_ANALYZER_NUMBER_OBJECT_CONVERSION = YES_AGGRESSIVE;
\t\t\t\tCLANG_CXX_LANGUAGE_STANDARD = "gnu++20";
\t\t\t\tCLANG_ENABLE_MODULES = YES;
\t\t\t\tCLANG_ENABLE_OBJC_ARC = YES;
\t\t\t\tCLANG_ENABLE_OBJC_WEAK = YES;
\t\t\t\tCOPY_PHASE_STRIP = NO;
\t\t\t\tDEBUG_INFORMATION_FORMAT = dwarf;
\t\t\t\tENABLE_STRICT_OBJC_MSGSEND = YES;
\t\t\t\tENABLE_TESTABILITY = YES;
\t\t\t\tGCC_C_LANGUAGE_STANDARD = gnu17;
\t\t\t\tGCC_DYNAMIC_NO_PIC = NO;
\t\t\t\tGCC_NO_COMMON_BLOCKS = YES;
\t\t\t\tGCC_OPTIMIZATION_LEVEL = 0;
\t\t\t\tGCC_PREPROCESSOR_DEFINITIONS = (
\t\t\t\t\t"DEBUG=1",
\t\t\t\t\t"$(inherited)",
\t\t\t\t);
\t\t\t\tGCC_WARN_64_TO_32_BIT_CONVERSION = YES;
\t\t\t\tGCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
\t\t\t\tGCC_WARN_UNDECLARED_SELECTOR = YES;
\t\t\t\tGCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
\t\t\t\tGCC_WARN_UNUSED_FUNCTION = YES;
\t\t\t\tGCC_WARN_UNUSED_VARIABLE = YES;
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = %s;
\t\t\t\tMTL_ENABLE_DEBUG_INFO = INCLUDE_SOURCE;
\t\t\t\tMTL_FAST_MATH = YES;
\t\t\t\tONLY_ACTIVE_ARCH = YES;
\t\t\t\tSDKROOT = iphoneos;
\t\t\t\tSWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG;
\t\t\t\tSWIFT_OPTIMIZATION_LEVEL = "-Onone";
\t\t\t\tSWIFT_WARN_PRIVATE_OVERLOADS = YES;""" % DEPLOYMENT_TARGET

PROJECT_RELEASE_SETTINGS = """\
\t\t\t\tCLANG_ANALYZER_NONNULL = YES;
\t\t\t\tCLANG_ANALYZER_NUMBER_OBJECT_CONVERSION = YES_AGGRESSIVE;
\t\t\t\tCLANG_CXX_LANGUAGE_STANDARD = "gnu++20";
\t\t\t\tCLANG_ENABLE_MODULES = YES;
\t\t\t\tCLANG_ENABLE_OBJC_ARC = YES;
\t\t\t\tCLANG_ENABLE_OBJC_WEAK = YES;
\t\t\t\tCOPY_PHASE_STRIP = NO;
\t\t\t\tDEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
\t\t\t\tENABLE_NS_ASSERTIONS = NO;
\t\t\t\tENABLE_STRICT_OBJC_MSGSEND = YES;
\t\t\t\tGCC_C_LANGUAGE_STANDARD = gnu17;
\t\t\t\tGCC_NO_COMMON_BLOCKS = YES;
\t\t\t\tGCC_OPTIMIZATION_LEVEL = s;
\t\t\t\tGCC_WARN_64_TO_32_BIT_CONVERSION = YES;
\t\t\t\tGCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
\t\t\t\tGCC_WARN_UNDECLARED_SELECTOR = YES;
\t\t\t\tGCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
\t\t\t\tGCC_WARN_UNUSED_FUNCTION = YES;
\t\t\t\tGCC_WARN_UNUSED_VARIABLE = YES;
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = %s;
\t\t\t\tMTL_ENABLE_DEBUG_INFO = NO;
\t\t\t\tMTL_FAST_MATH = YES;
\t\t\t\tONLY_ACTIVE_ARCH = NO;
\t\t\t\tSDKROOT = iphoneos;
\t\t\t\tSWIFT_COMPILATION_CONDITIONS = "";
\t\t\t\tSWIFT_OPTIMIZATION_LEVEL = "-O";
\t\t\t\tSWIFT_WARN_PRIVATE_OVERLOADS = YES;""" % DEPLOYMENT_TARGET

APP_SETTINGS = """\
\t\t\t\tCODE_SIGN_ENTITLEMENTS = ScreenTranslator/ScreenTranslator.entitlements;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCURRENT_PROJECT_VERSION = 1;
\t\t\t\tENABLE_BITCODE = NO;
\t\t\t\tGENERATE_INFOPLIST_FILE = NO;
\t\t\t\tINFOPLIST_FILE = ScreenTranslator/Info.plist;
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = %s;
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/Frameworks",
\t\t\t\t);
\t\t\t\tMARKETING_VERSION = 1.0;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = %s;
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t\tTARGETED_DEVICE_FAMILY = "1,2";""" % (DEPLOYMENT_TARGET, APP_BUNDLE)

EXT_SETTINGS = """\
\t\t\t\tCODE_SIGN_ENTITLEMENTS = ScreenTranslatorBroadcast/ScreenTranslatorBroadcast.entitlements;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCURRENT_PROJECT_VERSION = 1;
\t\t\t\tENABLE_BITCODE = NO;
\t\t\t\tGENERATE_INFOPLIST_FILE = NO;
\t\t\t\tINFOPLIST_FILE = ScreenTranslatorBroadcast/Info.plist;
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = %s;
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/Frameworks",
\t\t\t\t\t"@executable_path/../../Frameworks",
\t\t\t\t);
\t\t\t\tMARKETING_VERSION = 1.0;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = %s;
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSKIP_INSTALL = YES;
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t\tTARGETED_DEVICE_FAMILY = "1,2";""" % (DEPLOYMENT_TARGET, EXT_BUNDLE)


def xcconfig(uid_key, name, settings):
    w("\t\t%s /* %s */ = {" % (uid_key, name))
    w("\t\t\tisa = XCBuildConfiguration;")
    w("\t\t\tbuildSettings = {")
    w(settings)
    w("\t\t\t};")
    w("\t\t\tname = %s;" % name)
    w("\t\t};")


xcconfig(proj_debug, "Debug", PROJECT_DEBUG_SETTINGS)
xcconfig(proj_release, "Release", PROJECT_RELEASE_SETTINGS)
xcconfig(app_debug, "Debug", APP_SETTINGS)
xcconfig(app_release, "Release", APP_SETTINGS)
xcconfig(ext_debug, "Debug", EXT_SETTINGS)
xcconfig(ext_release, "Release", EXT_SETTINGS)
endcomment("XCBuildConfiguration section")
w()

# --- XCConfigurationList ---
comment("XCConfigurationList section")


def configlist(uid_key, name, debug, release):
    w("\t\t%s /* Build configuration list for %s */ = {" % (uid_key, name))
    w("\t\t\tisa = XCConfigurationList;")
    w("\t\t\tbuildConfigurations = (")
    w("\t\t\t\t%s /* Debug */," % debug)
    w("\t\t\t\t%s /* Release */," % release)
    w("\t\t\t);")
    w("\t\t\tdefaultConfigurationIsVisible = 0;")
    w("\t\t\tdefaultConfigurationName = Release;")
    w("\t\t};")


configlist(proj_list_uid, "PBXProject", proj_debug, proj_release)
configlist(app_list_uid, APP_TARGET, app_debug, app_release)
configlist(ext_list_uid, EXT_TARGET, ext_debug, ext_release)
endcomment("XCConfigurationList section")
w()

# ---------------------------------------------------------------------------
# Assemble final pbxproj
# ---------------------------------------------------------------------------
pbx = []
pbx.append("// !$*UTF8*$!")
pbx.append("{")
pbx.append("\tarchiveVersion = 1;")
pbx.append("\tclasses = {")
pbx.append("\t};")
pbx.append("\tobjectVersion = 56;")
pbx.append("\tobjects = {")
pbx.extend(L)
pbx.append("\t};")
pbx.append("\trootObject = %s /* Project object */;" % proj_uid)
pbx.append("}")

pbxproj_text = "\n".join(pbx) + "\n"

# ---------------------------------------------------------------------------
# Write files
# ---------------------------------------------------------------------------
xcodeproj = os.path.join(ROOT, PROJECT_NAME + ".xcodeproj")
os.makedirs(xcodeproj, exist_ok=True)
with open(os.path.join(xcodeproj, "project.pbxproj"), "w", encoding="utf-8") as f:
    f.write(pbxproj_text)

# Workspace
ws = os.path.join(xcodeproj, "project.xcworkspace")
os.makedirs(ws, exist_ok=True)
with open(os.path.join(ws, "contents.xcworkspacedata"), "w", encoding="utf-8") as f:
    f.write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Workspace\n'
        '   version = "1.0">\n'
        '   <FileRef\n'
        '      location = "self:">\n'
        '   </FileRef>\n'
        '</Workspace>\n'
    )

# Shared schemes
scheme_dir = os.path.join(xcodeproj, "xcshareddata", "xcschemes")
os.makedirs(scheme_dir, exist_ok=True)


def scheme(name, target_uid, product_name, is_app):
    build_for = 'buildForTesting="NO" buildForRunning="YES" buildForProfiling="YES" buildForArchiving="YES" buildForAnalyzing="YES"'
    body = []
    body.append('<?xml version="1.0" encoding="UTF-8"?>')
    body.append('<Scheme LastUpgradeVersion="1500" version="1.7">')
    body.append('   <BuildAction parallelizeBuildables="YES" buildImplicitDependencies="YES">')
    body.append('      <BuildActionEntries>')
    body.append('         <BuildActionEntry ' + build_for + '>')
    body.append('            <BuildableReference')
    body.append('               BuildableIdentifier = "primary"')
    body.append('               BlueprintIdentifier = "%s"' % target_uid)
    body.append('               BuildableName = "%s"' % product_name)
    body.append('               BlueprintName = "%s"' % name)
    body.append('               ReferencedContainer = "container:%s.xcodeproj">' % PROJECT_NAME)
    body.append('            </BuildableReference>')
    body.append('         </BuildActionEntry>')
    body.append('      </BuildActionEntries>')
    body.append('   </BuildAction>')
    body.append('   <TestAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.DebuggerFoundation.Launcher.LLDB" shouldUseLaunchSchemeArgsEnv="YES">')
    body.append('      <Testables>')
    body.append('      </Testables>')
    body.append('   </TestAction>')
    if is_app:
        body.append('   <LaunchAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.DebuggerFoundation.Launcher.LLDB" launchStyle="0" useCustomWorkingDirectory="NO" ignoresPersistentStateOnLaunch="NO" debugDocumentVersioning="YES" debugServiceExtension="internal" allowLocationSimulation="YES">')
        body.append('      <BuildableProductRunnable runnableDebuggingMode="0">')
        body.append('         <BuildableReference')
        body.append('            BuildableIdentifier = "primary"')
        body.append('            BlueprintIdentifier = "%s"' % target_uid)
        body.append('            BuildableName = "%s"' % product_name)
        body.append('            BlueprintName = "%s"' % name)
        body.append('            ReferencedContainer = "container:%s.xcodeproj">' % PROJECT_NAME)
        body.append('         </BuildableReference>')
        body.append('      </BuildableProductRunnable>')
        body.append('   </LaunchAction>')
    else:
        body.append('   <LaunchAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.DebuggerFoundation.Launcher.LLDB" launchStyle="0" useCustomWorkingDirectory="NO" ignoresPersistentStateOnLaunch="NO" debugDocumentVersioning="YES" debugServiceExtension="internal" allowLocationSimulation="YES">')
        body.append('   </LaunchAction>')
    body.append('   <ProfileAction buildConfiguration="Release" shouldUseLaunchSchemeArgsEnv="YES" savedToolIdentifier="" useCustomWorkingDirectory="NO" debugDocumentVersioning="YES">')
    if is_app:
        body.append('      <BuildableProductRunnable runnableDebuggingMode="0">')
        body.append('         <BuildableReference')
        body.append('            BuildableIdentifier = "primary"')
        body.append('            BlueprintIdentifier = "%s"' % target_uid)
        body.append('            BuildableName = "%s"' % product_name)
        body.append('            BlueprintName = "%s"' % name)
        body.append('            ReferencedContainer = "container:%s.xcodeproj">' % PROJECT_NAME)
        body.append('         </BuildableReference>')
        body.append('      </BuildableProductRunnable>')
    body.append('   </ProfileAction>')
    body.append('   <AnalyzeAction buildConfiguration="Debug">')
    body.append('   </AnalyzeAction>')
    body.append('   <ArchiveAction buildConfiguration="Release" revealArchiveInOrganizer="YES">')
    body.append('   </ArchiveAction>')
    body.append('</Scheme>')
    body.append("")
    return "\n".join(body)


with open(os.path.join(scheme_dir, APP_TARGET + ".xcscheme"), "w", encoding="utf-8") as f:
    f.write(scheme(APP_TARGET, app_target_uid, APP_TARGET + ".app", True))
with open(os.path.join(scheme_dir, EXT_TARGET + ".xcscheme"), "w", encoding="utf-8") as f:
    f.write(scheme(EXT_TARGET, ext_target_uid, EXT_TARGET + ".appex", False))

print("Generated:")
print("  " + os.path.join(xcodeproj, "project.pbxproj"))
print("  " + os.path.join(ws, "contents.xcworkspacedata"))
print("  " + os.path.join(scheme_dir, APP_TARGET + ".xcscheme"))
print("  " + os.path.join(scheme_dir, EXT_TARGET + ".xcscheme"))
