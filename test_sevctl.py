#!/usr/bin/env python3

import os
import shutil
import subprocess
import tempfile

import pytest

@pytest.fixture
def sevctl_bin():
    bin = os.environ.get("SEVCTL")
    if bin is not None:
        return bin
    bin = shutil.which("sevctl")
    if bin is None:
        print("sevctl binary not found")
        assert False

    return bin

@pytest.fixture
def unshare_bin():
    bin = os.environ.get("UNSHARE")
    if bin is not None:
        return bin
    bin = shutil.which("unshare")
    if bin is None:
        print("unshare binary not found")
        assert False

    return bin

@pytest.fixture
def dev_sev_r(dev_sev):
    try:
        with open(dev_sev, 'rb') as f:
            return True
    except:
        return False

@pytest.fixture
def dev_sev_w(dev_sev):
    try:
        with open(dev_sev, 'wb') as f:
            return True
    except:
        return False

@pytest.fixture
def dev_sev():
    return '/dev/sev'

def test_sevctl_export_emits_error_during_network_failure(sevctl_bin, unshare_bin, dev_sev_r):
    if not dev_sev_r:
        pytest.skip("unable to open /dev/sev")
    res = subprocess.run([unshare_bin, "-r", "-n", sevctl_bin, 'export', 'test.file'])
    assert res.returncode != 0

def test_sevctl_export_fails_on_hardware_without_sev_capability(sevctl_bin, dev_sev_r):
    if dev_sev_r:
        pytest.skip("/dev/sev is accessible but for this test it must not be")
    res = subprocess.run([sevctl_bin, "export", "test_file"])
    assert res.returncode != 0

@pytest.mark.skip(reason="AMD key server rate-limits test suite; adding backoff upstream: https://github.com/enarx/sevctl/issues/30")
def test_sevctl_export_full_chain_creates_file_at_specified_location(sevctl_bin, dev_sev_r):
    if not dev_sev_r:
        pytest.skip("unable to open /dev/sev")

    with tempfile.TemporaryDirectory() as tdir:
        fname = f"{tdir}/chain"
        res = subprocess.run([sevctl_bin, "export", "--full", str(fname)])
        assert res.returncode == 0

        st = os.stat(str(fname))
        assert st.st_size != 0

@pytest.mark.skip(reason="AMD key server rate-limits test suite; adding backoff upstream: https://github.com/enarx/sevctl/issues/30")
def test_sevctl_export_sev_chain_creates_file_at_specified_location(sevctl_bin, dev_sev_r):
    if not dev_sev_r:
        pytest.skip("unable to open /dev/sev")

    with tempfile.TemporaryDirectory() as tdir:
        fname = f"{tdir}/chain"
        res = subprocess.run([sevctl_bin, "export", str(fname)])
        assert res.returncode == 0

        st = os.stat(str(fname))
        assert st.st_size != 0

@pytest.mark.skip(reason="AMD key server rate-limits test suite; adding backoff upstream: https://github.com/enarx/sevctl/issues/30")
def test_sevctl_export_full_chain_fails_if_permissions_are_incorrect(sevctl_bin, dev_sev_r):
    if not dev_sev_r:
        pytest.skip("unable to open /dev/sev")

    with tempfile.TemporaryDirectory() as tdir:
        fname = f"{tdir}/full-chain"
        os.chmod(tdir, 0o577)
        res = subprocess.run([sevctl_bin, "export", "--full", fname])
        assert res.returncode != 0
        assert not os.path.exists(fname)

@pytest.mark.skip(reason="AMD key server rate-limits test suite; adding backoff upstream: https://github.com/enarx/sevctl/issues/30")
def test_sevctl_export_chain_fails_if_permissions_are_incorrect(sevctl_bin, dev_sev_r):
    if not dev_sev_r:
        pytest.skip("unable to open /dev/sev")

    with tempfile.TemporaryDirectory() as tdir:
        fname = f"{tdir}/chain"
        os.chmod(tdir, 0o577)
        res = subprocess.run([sevctl_bin, "export", fname])
        assert res.returncode != 0
        assert not os.path.exists(fname)

def test_sevctl_generate_ok(sevctl_bin, dev_sev_r):
    if not dev_sev_r:
        pytest.skip("unable to open /dev/sev")

        with tempfile.TemporaryDirectory() as tdir:
            cert = f"{tdir}/cert"
            key = f"{tdir}/key"

            res = subprocess.run([sevctl_bin, "generate", cert, key])
            assert res.returncode == 0
            assert os.path.exists(cert)
            assert os.path.exists(key)

def test_sevctl_generate_fails_if_perms_are_bad_for_cert(sevctl_bin, dev_sev_r):
    if not dev_sev_r:
        pytest.skip("unable to open /dev/sev")

    with tempfile.TemporaryDirectory() as tdir:
        eperm = os.mkdir(f"{tdir}/eperm", 0o577)
        cert = f"{eperm}/cert"
        key = f"{tdir}/key"

        res = subprocess.run([sevctl_bin, "generate", cert, key])
        assert res.returncode != 0
        assert not os.path.exists(cert)
        assert not os.path.exists(key)

def test_sevctl_generate_fails_if_perms_are_bad_for_key(sevctl_bin, dev_sev_r):
    if not dev_sev_r:
        pytest.skip("unable to open /dev/sev")

    with tempfile.TemporaryDirectory() as tdir:
        eperm = os.mkdir(f"{tdir}/eperm", 0o577)
        cert = f"{tdir}/cert"
        key = f"{eperm}/key"

        res = subprocess.run([sevctl_bin, "generate", cert, key])
        assert res.returncode != 0
        assert not os.path.exists(key)

def test_sevctl_reset_on_sev_hardware(sevctl_bin, dev_sev_w):
    if not dev_sev_w:
        pytest.skip("does not have write-access to /dev/sev")

    res = subprocess.run([sevctl_bin, "reset"])
    assert res.returncode == 0

def test_sevctl_reset_on_non_sev_hardware(sevctl_bin, dev_sev_w, dev_sev_r):
    if dev_sev_w or dev_sev_r:
        pytest.skip("/dev/sev is accessible but for this test it must not be")

    res = subprocess.run([sevctl_bin, "reset"])
    assert res.returncode != 0

def test_sevctl_rotate_on_sev_capable_hardware(sevctl_bin, dev_sev_w):
    if not dev_sev_w:
        pytest.skip("does not have write-access to /dev/sev")

    res = subprocess.run([sevctl_bin, "rotate"])
    assert res.returncode == 0

def test_sevctl_rotate_on_non_sev_hardware(sevctl_bin, dev_sev_w, dev_sev_r):
    if dev_sev_w or dev_sev_r:
        pytest.skip("/dev/sev is accessible but for this test it must not be")

    res = subprocess.run([sevctl_bin, "rotate"])
    assert res.returncode != 0

def test_sevctl_show_fails_on_non_sev_hardware(sevctl_bin, dev_sev_r):
    if dev_sev_r:
        pytest.skip("/dev/sev is accessible but for this test it must not be")

    res = subprocess.run([sevctl_bin, "show", "guests"])
    assert res.returncode != 0

    res = subprocess.run([sevctl_bin, "show", "flags"])
    assert res.returncode != 0

def test_sevctl_show_exits_cleanly_on_sev_hardware(sevctl_bin, dev_sev_r):
    if not dev_sev_r:
        pytest.skip("unable to open /dev/sev")

    res = subprocess.run([sevctl_bin, "show", "guests"])
    assert res.returncode == 0

    res = subprocess.run([sevctl_bin, "show", "flags"])
    assert res.returncode == 0

def test_sevctl_verify_sev_file_does_not_exist(sevctl_bin):
    res = subprocess.run([sevctl_bin, "verify", "--sev", "does-not-exist"])
    assert res.returncode != 0

def test_sevctl_verify_other_certs_dont_exist(sevctl_bin, dev_sev_r):
    if not dev_sev_r:
        pytest.skip("unable to open /dev/sev")

    res = subprocess.run([sevctl_bin, "verify", "--sev", "sev-good.chain", "--oca", "does-not-exist"])
    assert res.returncode != 0

    res = subprocess.run([sevctl_bin, "verify", "--sev", "sev-good.chain", "--ca", "does-not-exist"])
    assert res.returncode != 0

def test_sevctl_verify_invalid_certs(sevctl_bin, dev_sev_r):
    if not dev_sev_r:
        pytest.skip("unable to open /dev/sev")

    res = subprocess.run([sevctl_bin, "verify", "--sev", "sev-bad.chain"])
    assert res.returncode != 0

    res = subprocess.run([sevctl_bin, "verify", "--sev", "sev-good.chain", "--oca", "oca-bad.chain"])
    assert res.returncode != 0

def test_sevctl_verify_eperm(sevctl_bin, dev_sev_r):
    if not dev_sev_r:
        pytest.skip("unable to open /dev/sev")

    with tempfile.TemporaryDirectory() as tdir:
        sevf = f"{tdir}/sev.chain"
        shutil.copyfile("sev-good.chain", sevf)
        os.chmod(sevf, 0o277)

        res = subprocess.run([sevctl_bin, "verify", "--sev", sevf])
        assert res.returncode != 0

        res = subprocess.run([sevctl_bin, "verify", "--sev", "sev-good.chain", "--oca", sevf])
        assert res.returncode != 0

        res = subprocess.run([sevctl_bin, "verify", "--sev", "sev-good.chain", "--ca", sevf])
        assert res.returncode != 0

def test_sevctl_verify_emits_error_during_network_failure(sevctl_bin, unshare_bin, dev_sev_r):
    if not dev_sev_r:
        pytest.skip("unable to open /dev/sev")
    res = subprocess.run([unshare_bin, "-r", "-n", sevctl_bin, "verify"])
    assert res.returncode != 0

@pytest.mark.skip(reason="AMD key server rate-limits test suite; adding backoff upstream: https://github.com/enarx/sevctl/issues/30")
def test_sevctl_verify_ok(sevctl_bin, dev_sev_r):
    if not dev_sev_r:
        pytest.skip("unable to open /dev/sev")
    res = subprocess.run([sevctl_bin, "verify"])
    assert res.returncode == 0