# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import pytest

from shuup.xtheme import Plugin
from shuup.xtheme.resources import (
    add_resource, inject_resources, InlineMarkupResource, InlineScriptResource,
    RESOURCE_CONTAINER_VAR_NAME, ResourceContainer
)
from shuup.xtheme.testing import override_current_theme_class
from shuup_tests.xtheme.utils import (
    get_jinja2_engine, get_request, get_test_template_bits, plugin_override
)


class ResourceInjectorPlugin(Plugin):
    identifier = "inject"
    message = "I've injected some resources into this page."
    meta_markup = "<meta data-meta=\"so meta\">"
    editor_form_class = None  # Explicitly no form class here :)

    def render(self, context):
        add_resource(context, "body_start", "://example.com/js.js")
        add_resource(context, "body_start", "://foo/fuzz.png")
        add_resource(context, "head_end", "://example.com/css.css")
        add_resource(context, "body_end", InlineScriptResource("alert('xss')"))
        add_resource(context, "head_end", InlineScriptResource.from_vars("foos", {"bars": (1, 2, 3)}))
        add_resource(context, "head_end", InlineMarkupResource(self.meta_markup))
        add_resource(context, "head_end", InlineMarkupResource(self.meta_markup))  # Test duplicates
        add_resource(context, "head_end", "")  # Test the no-op branch
        add_resource(context, "content_start", InlineMarkupResource("START"))
        add_resource(context, "content_end", InlineMarkupResource("END"))
        return self.message


def test_injecting_into_weird_places():
    request = get_request()
    (template, layout, gibberish, ctx) = get_test_template_bits(request, **{
        RESOURCE_CONTAINER_VAR_NAME: ResourceContainer()
    })
    with pytest.raises(ValueError):
        add_resource(ctx, "yes", "hello.js")


def test_without_rc():
    request = get_request()
    (template, layout, gibberish, ctx) = get_test_template_bits(request)
    assert not add_resource(ctx, "yes", "hello.js")
    content1 = "<html>"
    content2 = inject_resources(ctx, content1)
    assert content1 == content2
